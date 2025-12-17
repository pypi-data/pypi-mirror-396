from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Protocol, List, Set
from pathlib import Path


class MigrationStatus(Enum):
    PENDING = "pending"
    APPLIED = "applied"
    FAILED = "failed"


@dataclass
class Migration:
    """Domain model for a migration"""
    version: str
    description: str
    sql_up: Optional[str] = None
    sql_down: Optional[str] = None
    created_at: datetime = None
    applied_at: Optional[datetime] = None
    status: MigrationStatus = MigrationStatus.PENDING
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    url: str
    migrations_dir: Path = Path("./migrations")
    schema_table: str = "schema_migrations"    
    schema_file: Path = Path("./schema.sql")
    models_path: Optional[str] = "models"  # Python module path
    models_file: Optional[Path] = None     # Or specific file    
    echo: bool = False

    # Tables to exclude from migrations
    exclude_tables: Set[str] = field(default_factory=set)
    
    # Patterns to exclude (supports wildcards)
    exclude_patterns: List[str] = field(default_factory=list)    
    
    def __post_init__(self):
        self.migrations_dir = Path(self.migrations_dir)
        self.schema_file = Path(self.schema_file)
        if self.models_file:
            self.models_file = Path(self.models_file)     

        # Always exclude the schema migrations table
        self.exclude_tables.add(self.schema_table)
        
        # Add any environment-defined exclusions
        self._load_exclusions_from_env()                

    def _load_exclusions_from_env(self):
        """Load table exclusions from environment variables"""
        import os
        
        # Load comma-separated table names
        exclude_tables_env = os.getenv('EXCLUDE_TABLES', '')
        if exclude_tables_env:
            for table in exclude_tables_env.split(','):
                table = table.strip()
                if table:
                    self.exclude_tables.add(table)
        
        # Load comma-separated patterns
        exclude_patterns_env = os.getenv('EXCLUDE_PATTERNS', '')
        if exclude_patterns_env:
            for pattern in exclude_patterns_env.split(','):
                pattern = pattern.strip()
                if pattern:
                    self.exclude_patterns.append(pattern)     

    def should_exclude_table(self, table_name: str) -> bool:
        """Check if a table should be excluded from migrations"""
        # Check exact matches
        if table_name in self.exclude_tables:
            return True
        
        # Check patterns (supports * wildcard)
        for pattern in self.exclude_patterns:
            if self._match_pattern(pattern, table_name):
                return True
        
        return False       

    def _match_pattern(self, pattern: str, table_name: str) -> bool:
        """Match table name against pattern with * wildcard support"""
        import re
        
        # Convert pattern to regex
        # * becomes .*
        # ? becomes .
        regex_pattern = pattern.replace('*', '.*').replace('?', '.')
        regex_pattern = f"^{regex_pattern}$"
        
        return bool(re.match(regex_pattern, table_name, re.IGNORECASE))                    


class MigrationRepository(Protocol):
    """Interface for migration storage"""
    async def create_migrations_table(self) -> None: ...
    async def get_applied_migrations(self) -> list[Migration]: ...
    async def record_migration(self, migration: Migration) -> None: ...
    async def remove_migration(self, version: str) -> None: ...
    async def get_pending_migrations(self) -> list[Migration]: ...        