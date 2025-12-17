from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from datetime import datetime
import logging

from sqlalchemy import (
    MetaData, Table, Column, String, DateTime, 
    create_engine, text, inspect, Engine
)
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncEngine, AsyncConnection
)
from sqlalchemy.pool import NullPool

from ..config import Migration, MigrationStatus, DatabaseConfig

logger = logging.getLogger(__name__)


class DatabaseAdapter:
    """SQLAlchemy database adapter with migration support"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.metadata = MetaData()
        self._engine: Optional[AsyncEngine] = None
        self._sync_engine: Optional[Engine] = None
        
        # Define schema migrations table
        self.migrations_table = Table(
            config.schema_table,
            self.metadata,
            Column('version', String(255), primary_key=True),
            Column('applied_at', DateTime, nullable=False),
        )
    
    @property
    def engine(self) -> AsyncEngine:
        if not self._engine:
            self._engine = create_async_engine(
                self.config.url,
                echo=self.config.echo,
                poolclass=NullPool,  # Avoid connection pool issues
            )
        return self._engine
    
    @property
    def sync_engine(self) -> Engine:
        """Sync engine for Alembic operations"""
        if not self._sync_engine:
            # Convert async URL to sync
            sync_url = self.config.url.replace('+asyncpg', '').replace('+aiomysql', '')
            self._sync_engine = create_engine(
                sync_url,
                echo=self.config.echo,
                poolclass=NullPool,
            )
        return self._sync_engine
    
    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[AsyncConnection, None]:
        async with self.engine.begin() as conn:
            yield conn
    
    async def create_database(self) -> None:
        """Create database if it doesn't exist"""
        # Parse database name from URL
        db_name = self.config.url.split('/')[-1].split('?')[0]
        base_url = '/'.join(self.config.url.split('/')[:-1])
        
        # Connect to default database
        #admin_url = f"{base_url}/postgres" if 'postgresql' in base_url else base_url
        admin_engine = self.engine #create_async_engine(admin_url, isolation_level='AUTOCOMMIT')
        
        try:
            async with admin_engine.connect() as conn:
                # Check if database exists
                result = await conn.execute(
                    text(f"SELECT 1 FROM pg_database WHERE datname = :db_name"),
                    {"db_name": db_name}
                )
                if not result.first():
                    await conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                    logger.info(f"Database '{db_name}' created successfully")
        finally:
            await admin_engine.dispose()
    
    async def create_migrations_table(self) -> None:
        """Create schema migrations table if it doesn't exist"""
        async with self.connection() as conn:
            await conn.run_sync(self.metadata.create_all)
            logger.info(f"Migrations table '{self.config.schema_table}' ready")
    
    async def get_applied_migrations(self) -> list[str]:
        """Get list of applied migration versions"""
        async with self.connection() as conn:
            result = await conn.execute(
                self.migrations_table.select().order_by(
                    self.migrations_table.c.version
                )
            )
            return [row.version for row in result]
    
    async def record_migration(self, version: str) -> None:
        """Record a migration as applied"""
        async with self.connection() as conn:
            await conn.execute(
                self.migrations_table.insert().values(
                    version=version,
                    applied_at=datetime.utcnow()
                )
            )
            logger.info(f"Migration {version} recorded as applied")
    
    async def remove_migration(self, version: str) -> None:
        """Remove a migration record"""
        async with self.connection() as conn:
            await conn.execute(
                self.migrations_table.delete().where(
                    self.migrations_table.c.version == version
                )
            )
            logger.info(f"Migration {version} removed from history")
    
    async def execute_sql(self, sql: str) -> None:
        """Execute raw SQL"""
        async with self.connection() as conn:
            for statement in sql.split(';'):
                if statement.strip():
                    await conn.execute(text(statement))
    
    async def close(self) -> None:
        """Close database connections"""
        if self._engine:
            await self._engine.dispose()
        if self._sync_engine:
            self._sync_engine.dispose()