# core/adapters/alembic.py (refactored)
from typing import Optional, Tuple, List
import logging
from datetime import datetime

from alembic.runtime.migration import MigrationContext
from alembic.autogenerate.api import  produce_migrations
from alembic.operations import ops
from sqlalchemy import MetaData, text
from sqlalchemy.schema import CreateTable, DropTable, CreateIndex, DropIndex, CreateColumn
from sqlalchemy.schema import AddConstraint, DropConstraint
from sqlalchemy.dialects import postgresql, mysql, sqlite

from ..config import DatabaseConfig
from ..services.model_loader import ModelLoader

logger = logging.getLogger(__name__)


class AlembicAdapter:
    """Alembic integration using SQLAlchemy DDL compiler"""
    
    def __init__(self, config: DatabaseConfig, db_adapter):
        self.config = config
        self.db_adapter = db_adapter
        self.model_loader = ModelLoader()
        self.target_metadata: Optional[MetaData] = None
        
        # Detect dialect from URL
        self.dialect = self._get_dialect()
    
    def _get_dialect(self):
        """Get SQLAlchemy dialect from database URL"""
        url = self.config.url.lower()
        
        if 'postgresql' in url or 'postgres' in url:
            return postgresql.dialect()
        elif 'mysql' in url or 'mariadb' in url:
            return mysql.dialect()
        elif 'sqlite' in url:
            return sqlite.dialect()
        else:
            # Default to postgresql
            logger.warning(f"Unknown dialect for URL: {url}, using PostgreSQL")
            return postgresql.dialect()
        
    def _filter_metadata(self, metadata: MetaData) -> MetaData:
        """Filter out excluded tables from metadata"""
        filtered_metadata = MetaData()
        
        for table_name, table in metadata.tables.items():
            # Extract just the table name (without schema prefix)
            simple_name = table_name.split('.')[-1]
            
            if not self.config.should_exclude_table(simple_name):
                # Copy table to filtered metadata
                table.to_metadata(filtered_metadata)
            else:
                logger.debug(f"Excluding table from migrations: {table_name}")
        
        return filtered_metadata        
    
    def load_models(self) -> MetaData:
        """Load user models with exclusions applied"""
        if self.target_metadata:
            return self.target_metadata
        
        # Load models from configured source
        if self.config.models_file:
            raw_metadata = self.model_loader.load_from_file(self.config.models_file)
        elif self.config.models_path:
            raw_metadata = self.model_loader.load_from_module(self.config.models_path)
        else:
            logger.info("Auto-discovering models...")
            raw_metadata = self._auto_discover_models()
        
        # Apply exclusions
        self.target_metadata = self._filter_metadata(raw_metadata)
        
        logger.info(f"Loaded {len(self.target_metadata.tables)} tables (after exclusions)")
        
        return self.target_metadata
    
    def _get_database_metadata(self) -> MetaData:
        """Get current database metadata with exclusions"""
        from sqlalchemy import inspect
        from sqlalchemy import Table
        
        db_metadata = MetaData()
        
        with self.db_adapter.sync_engine.connect() as connection:
            inspector = inspect(connection)
            
            # Get all table names
            table_names = inspector.get_table_names()
            
            for table_name in table_names:
                # Skip excluded tables
                if self.config.should_exclude_table(table_name):
                    logger.debug(f"Excluding existing table: {table_name}")
                    continue
                
                # Reflect table structure
                Table(table_name, db_metadata, autoload_with=connection)
        
        return db_metadata    
    
    def _auto_discover_models(self) -> MetaData:
        """Auto-discover models from common locations"""
        search_patterns = [
            "models.py",
            "*/models.py",
            "app/models/*.py",
            "src/models/*.py",
        ]
        
        combined_metadata = MetaData()
        
        for pattern in search_patterns:
            try:
                metadata = self.model_loader.load_from_pattern(pattern)
                for table in metadata.tables.values():
                    table.to_metadata(combined_metadata)
            except Exception:
                pass
        
        return combined_metadata
    
    def _filter_operations(self, operations: List) -> List:
        """Filter operations to exclude certain tables"""
        filtered = []
        
        for op in operations:
            # Check table operations
            if isinstance(op, (ops.CreateTableOp, ops.DropTableOp)):
                if self.config.should_exclude_table(op.table_name):
                    logger.debug(f"Filtering out operation for excluded table: {op.table_name}")
                    continue
            
            # Check column operations
            elif isinstance(op, (ops.AddColumnOp, ops.DropColumnOp, ops.AlterColumnOp)):
                if hasattr(op, 'table_name') and self.config.should_exclude_table(op.table_name):
                    logger.debug(f"Filtering out column operation for excluded table: {op.table_name}")
                    continue
            
            # Check index operations
            elif isinstance(op, (ops.CreateIndexOp, ops.DropIndexOp)):
                table_name = getattr(op, 'table_name', None)
                if table_name and self.config.should_exclude_table(table_name):
                    logger.debug(f"Filtering out index operation for excluded table: {table_name}")
                    continue
            
            # Check constraint operations
            elif isinstance(op, (ops.CreateForeignKeyOp, ops.DropConstraintOp)):
                source_table = getattr(op, 'source_table', getattr(op, 'table_name', None))
                if source_table and self.config.should_exclude_table(source_table):
                    logger.debug(f"Filtering out constraint operation for excluded table: {source_table}")
                    continue
            
            filtered.append(op)
        
        return filtered    
    
    def generate_migration(
        self, 
        name: str,
        auto_generate: bool = True
    ) -> Tuple[str, str, str]:
        """Generate migration using SQLAlchemy DDL compiler"""
        version = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        
        if not auto_generate:
            return version, "", ""
        
        target_metadata = self.load_models()

        if not target_metadata.tables:
            logger.warning("No models found after exclusions")
            return version, "", ""        
        
        # Get diff operations with exclusions
        diff_ops = self._get_diff_operations(target_metadata)
                
        if not diff_ops:
            logger.info("No changes detected")
            return version, "", ""
        
        # Log what's being migrated
        self._log_migration_summary(diff_ops)
        
        # Convert to SQL using SQLAlchemy DDL compiler
        up_sql = self._generate_sql_from_ops(diff_ops, upgrade=True)
        down_sql = self._generate_sql_from_ops(diff_ops, upgrade=False)
        
        return version, up_sql, down_sql
    
    def _log_migration_summary(self, operations: List):
        """Log summary of migration operations"""
        create_tables = [op.table_name for op in operations if isinstance(op, ops.CreateTableOp)]
        drop_tables = [op.table_name for op in operations if isinstance(op, ops.DropTableOp)]
        
        if create_tables:
            logger.info(f"Creating tables: {', '.join(create_tables)}")
        if drop_tables:
            logger.info(f"Dropping tables: {', '.join(drop_tables)}")
        
        # Count other operations
        other_ops = len([op for op in operations 
                         if not isinstance(op, (ops.CreateTableOp, ops.DropTableOp))])
        if other_ops:
            logger.info(f"Plus {other_ops} other operations")    
    
    def _compare_metadata(self, context: MigrationContext, metadata: MetaData) -> Any:
            migration_script = produce_migrations(context, metadata)
            assert migration_script.upgrade_ops is not None
            return migration_script.upgrade_ops.ops
    
    def _get_diff_operations(self, target_metadata: MetaData) -> List:
        """Get diff operations from Alembic comparison"""
        with self.db_adapter.sync_engine.connect() as connection:
            mc = MigrationContext.configure(
                connection,
                opts={
                    'compare_type': True,
                    'compare_server_default': True
                }
            )

            # Get filtered database metadata
            self._get_database_metadata()

            # Compare using filtered metadata
            diff_ops = self._compare_metadata(mc, target_metadata)

            # Additional filtering of operations
            filtered_ops = self._filter_operations(diff_ops)
            
            return filtered_ops
                
    def _generate_sql_from_ops(self, diff_ops: List, upgrade: bool = True) -> str:
        """Generate SQL from operations using SQLAlchemy DDL compiler"""
        sql_statements = []
        
        # Process operations in correct order
        if not upgrade:
            diff_ops = list(reversed(diff_ops))
        
        for op in diff_ops:
            
            if isinstance(op, ops.ModifyTableOps):
                for sub_ops in op.ops:
                    sql = self._operation_to_sql(sub_ops, upgrade)
                    sql_statements.append(f"{sql};")

            else:            
                sql = self._operation_to_sql(op, upgrade)
                if sql:
                    sql_statements.append(f"{sql};")
        
        return '\n'.join(sql_statements)
    
    def _operation_to_sql(self, op, upgrade: bool = True) -> Optional[str]:
        """Convert single operation to SQL using SQLAlchemy DDL"""
        
        # Table operations
        if isinstance(op, ops.CreateTableOp):
            if upgrade:
                # Use SQLAlchemy's CreateTable DDL
                return self._compile_ddl(CreateTable(op.to_table()))
            else:
                return self._compile_ddl(DropTable(op.to_table()))
        
        elif isinstance(op, ops.DropTableOp):
            if upgrade:
                # Create a Table object for dropping
                from sqlalchemy import Table
                table = Table(op.table_name, MetaData())
                return self._compile_ddl(DropTable(table))
            else:
                return f"-- Cannot recreate dropped table {op.table_name} without schema"                 
        
        # Column operations
        elif isinstance(op, ops.AddColumnOp):
            if upgrade:                
                return self._add_column_sql(op)
            else:
                return self._drop_column_sql(op.table_name, op.column.name)
        
        elif isinstance(op, ops.DropColumnOp):
            if upgrade:
                return self._drop_column_sql(op.table_name, op.column_name)
            else:
                return f"-- Cannot recreate dropped column {op.column_name}"
        
        # Index operations
        elif isinstance(op, ops.CreateIndexOp):
            if upgrade:
                index = op.to_index()
                return self._compile_ddl(CreateIndex(index))
            else:
                index = op.to_index()
                return self._compile_ddl(DropIndex(index))
        
        elif isinstance(op, ops.DropIndexOp):
            if upgrade:
                from sqlalchemy import Index
                index = Index(op.index_name)
                return self._compile_ddl(DropIndex(index))
            else:
                return f"-- Cannot recreate dropped index {op.index_name}"
        
        # Constraint operations
        elif isinstance(op, ops.CreateForeignKeyOp):
            if upgrade:
                return self._create_foreign_key_sql(op)
            else:
                return self._drop_constraint_sql(op.constraint_name, op.source_table)
        
        elif isinstance(op, ops.CreateUniqueConstraintOp):
            if upgrade:
                constraint = op.to_constraint()
                return self._compile_ddl(AddConstraint(constraint))
            else:
                return self._drop_constraint_sql(op.constraint_name, op.table_name)
        
        # Alter column operations
        elif isinstance(op, ops.AlterColumnOp):
            return self._alter_column_sql(op, upgrade)
        
        return None
    
    def _compile_ddl(self, ddl_element) -> str:
        """Compile DDL element to SQL string using appropriate dialect"""
        return str(ddl_element.compile(dialect=self.dialect))
    
    def _add_column_sql(self, op: ops.AddColumnOp) -> str:
        """Generate ADD COLUMN SQL"""
        from sqlalchemy import Column
        
        # Create column from operation
        column = op.column
        
        # Build ALTER TABLE ADD COLUMN statement
        sql = f"ALTER TABLE {op.table_name} ADD COLUMN "
        
        # Column definition using dialect-specific compilation
        col_def = self._get_column_definition(column)
        
        return sql + col_def
    
    def _drop_column_sql(self, table_name: str, column_name: str) -> str:
        """Generate DROP COLUMN SQL"""
        return f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
    
    def _get_column_definition(self, column) -> str:
        """Get column definition SQL using dialect compiler"""
        from sqlalchemy.schema import CreateColumn
        
        # Use SQLAlchemy's CreateColumn DDL
        create_col = CreateColumn(column)
        col_sql = str(create_col.compile(dialect=self.dialect))
        
        # Extract just the column definition part
        # CreateColumn generates "column_name type constraints"
        return col_sql
    
    def _create_foreign_key_sql(self, op: ops.CreateForeignKeyOp) -> str:
        """Generate CREATE FOREIGN KEY SQL"""
        fk_name = op.constraint_name
        source_table = op.source_table
        source_cols = ", ".join(op.local_cols)
        target_table = op.referent_table
        target_cols = ", ".join(op.remote_cols)
        
        sql = f"ALTER TABLE {source_table} ADD CONSTRAINT {fk_name} "
        sql += f"FOREIGN KEY ({source_cols}) REFERENCES {target_table} ({target_cols})"
        
        if op.ondelete:
            sql += f" ON DELETE {op.ondelete}"
        if op.onupdate:
            sql += f" ON UPDATE {op.onupdate}"
        
        return sql
    
    def _drop_constraint_sql(self, constraint_name: str, table_name: str) -> str:
        """Generate DROP CONSTRAINT SQL"""
        return f"ALTER TABLE {table_name} DROP CONSTRAINT {constraint_name}"
    
    def _alter_column_sql(self, op: ops.AlterColumnOp, upgrade: bool) -> str:
        """Generate ALTER COLUMN SQL"""
        sqls = []
        
        # Type change
        if op.modify_type is not None:
            if upgrade:
                type_sql = str(op.modify_type.compile(dialect=self.dialect))
                sqls.append(
                    f"ALTER TABLE {op.table_name} "
                    f"ALTER COLUMN {op.column_name} TYPE {type_sql}"
                )
        
        # Nullable change
        if op.modify_nullable is not None:
            if op.modify_nullable:
                sqls.append(
                    f"ALTER TABLE {op.table_name} "
                    f"ALTER COLUMN {op.column_name} DROP NOT NULL"
                )
            else:
                sqls.append(
                    f"ALTER TABLE {op.table_name} "
                    f"ALTER COLUMN {op.column_name} SET NOT NULL"
                )
        
        # Default change
        if op.modify_server_default is not None:
            if op.modify_server_default:
                default_sql = str(op.modify_server_default.arg)
                sqls.append(
                    f"ALTER TABLE {op.table_name} "
                    f"ALTER COLUMN {op.column_name} SET DEFAULT {default_sql}"
                )
            else:
                sqls.append(
                    f"ALTER TABLE {op.table_name} "
                    f"ALTER COLUMN {op.column_name} DROP DEFAULT"
                )
        
        return ";\n".join(sqls) if sqls else ""