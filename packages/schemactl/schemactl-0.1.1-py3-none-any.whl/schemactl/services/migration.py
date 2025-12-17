# core/services/migration_service.py (rollback additions)
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple
import logging

from ..config import Migration, MigrationStatus, DatabaseConfig
from ..adapters.database import DatabaseAdapter
from ..adapters.alembic import AlembicAdapter

logger = logging.getLogger(__name__)


class MigrationService:
    """Core migration management service with rollback support"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.db = DatabaseAdapter(config)
        self.alembic = AlembicAdapter(config, self.db)
        
        self.config.migrations_dir.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self) -> None:
        """Initialize migration system"""
        await self.db.create_migrations_table()
    
    def generate_version(self) -> str:
        """Generate migration version (timestamp-based)"""
        return datetime.utcnow().strftime('%Y%m%d%H%M%S')
    
    def sanitize_name(self, name: str) -> str:
        """Sanitize migration name"""
        return re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
    
    async def new_migration(self, name: str) -> Path:
        """Create a new migration file"""
        version = self.generate_version()
        safe_name = self.sanitize_name(name)
        filename = f"{version}_{safe_name}.sql"
        filepath = self.config.migrations_dir / filename
        
        # Migration template
        template = f"""-- migrate:up
-- {name}


-- migrate:down
-- Rollback {name}

"""
        
        filepath.write_text(template)
        logger.info(f"Created migration: {filepath}")
        return filepath    
    
    def parse_migration_file(self, filepath: Path) -> Tuple[str, str]:
        """Parse migration file to extract UP and DOWN SQL"""
        content = filepath.read_text()
        
        # Split by migration markers
        up_match = re.search(r'-- migrate:up\n(.*?)(?=-- migrate:down|$)', content, re.DOTALL)
        down_match = re.search(r'-- migrate:down\n(.*?)$', content, re.DOTALL)
        
        up_sql = up_match.group(1).strip() if up_match else ""
        down_sql = down_match.group(1).strip() if down_match else ""
        
        # Remove empty comments and clean up
        up_sql = self._clean_sql(up_sql)
        down_sql = self._clean_sql(down_sql)
        
        return up_sql, down_sql
    
    def _clean_sql(self, sql: str) -> str:
        """Clean SQL by removing empty comments and extra whitespace"""
        if not sql:
            return ""
        
        lines = sql.split('\n')
        cleaned = []
        
        for line in lines:
            line = line.strip()
            # Skip empty comments but keep meaningful ones
            if line and not (line == '--' or line.startswith('-- TODO')):
                cleaned.append(line)
        
        return '\n'.join(cleaned)
    
    def get_migration_files(self) -> List[Path]:
        """Get all migration files sorted by version"""
        files = sorted(
            self.config.migrations_dir.glob("*.sql"),
            key=lambda f: f.stem.split('_')[0]
        )
        return files
    
    def get_migration_file_by_version(self, version: str) -> Optional[Path]:
        """Get specific migration file by version"""
        for filepath in self.get_migration_files():
            if filepath.stem.split('_')[0] == version:
                return filepath
        return None
    
    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions in order"""
        return await self.db.get_applied_migrations()
    
    async def get_last_migration(self) -> Optional[Tuple[str, Path]]:
        """Get the most recently applied migration"""
        applied = await self.get_applied_migrations()
        if not applied:
            return None
        
        # Get the last applied version
        last_version = applied[-1]
        filepath = self.get_migration_file_by_version(last_version)
        
        if not filepath:
            logger.warning(f"Migration file not found for version {last_version}")
            return None
        
        return last_version, filepath
    
    async def get_migrations_to_rollback(self, target: Optional[str] = None, steps: int = 1) -> List[Tuple[str, Path]]:
        """
        Get migrations that need to be rolled back
        
        Args:
            target: Roll back to this version (exclusive - this version stays)
            steps: Number of migrations to roll back (if target not specified)
        
        Returns:
            List of (version, filepath) tuples in reverse order
        """
        applied = await self.get_applied_migrations()
        if not applied:
            return []
        
        to_rollback = []
        
        if target:
            # Roll back to specific version
            found_target = False
            for version in reversed(applied):
                if version == target:
                    found_target = True
                    break
                
                filepath = self.get_migration_file_by_version(version)
                if filepath:
                    to_rollback.append((version, filepath))
                else:
                    logger.warning(f"Migration file not found for version {version}")
            
            if not found_target and target != '0':
                raise ValueError(f"Target version {target} not found in applied migrations")
        else:
            # Roll back specified number of steps
            for version in reversed(applied[-steps:]):
                filepath = self.get_migration_file_by_version(version)
                if filepath:
                    to_rollback.append((version, filepath))
                else:
                    logger.warning(f"Migration file not found for version {version}")
        
        return to_rollback
    
    async def rollback(
        self, 
        target: Optional[str] = None, 
        steps: int = 1,
        dry_run: bool = False
    ) -> int:
        """
        Roll back migrations
        
        Args:
            target: Roll back to this version (exclusive)
            steps: Number of migrations to roll back
            dry_run: Show what would be done without executing
        
        Returns:
            Number of migrations rolled back
        """
        await self.initialize()
        
        # Get migrations to roll back
        to_rollback = await self.get_migrations_to_rollback(target, steps)
        
        if not to_rollback:
            logger.info("No migrations to roll back")
            return 0
        
        if dry_run:
            logger.info(f"Would roll back {len(to_rollback)} migration(s):")
            for version, filepath in to_rollback:
                logger.info(f"  - {filepath.name}")
            return 0
        
        rolled_back = 0
        
        for version, filepath in to_rollback:
            logger.info(f"Rolling back migration: {filepath.name}")
            
            # Parse migration file to get down SQL
            _, down_sql = self.parse_migration_file(filepath)
            
            if not down_sql:
                logger.warning(f"⚠ No down migration found in {filepath.name}")
                if not await self._confirm_skip_empty():
                    raise ValueError(f"Aborting: No down migration in {filepath.name}")
                logger.info(f"Skipping {filepath.name}")
                continue
            
            try:
                # Execute down migration
                await self.db.execute_sql(down_sql)
                
                # Remove from migration history
                await self.db.remove_migration(version)
                
                rolled_back += 1
                logger.info(f"✓ Rolled back {filepath.name}")
                
            except Exception as e:
                logger.error(f"✗ Failed to rollback {filepath.name}: {e}")
                raise
        
        return rolled_back
    
    async def _confirm_skip_empty(self) -> bool:
        """Confirm skipping empty down migration (for CLI interaction)"""
        # In automated mode, we skip
        # This can be overridden by CLI to ask user
        return True
    
    async def rollback_all(self, dry_run: bool = False) -> int:
        """Roll back all applied migrations"""
        applied = await self.get_applied_migrations()
        
        if not applied:
            logger.info("No migrations to roll back")
            return 0
        
        # Roll back to version 0 (before any migrations)
        return await self.rollback(target='0', dry_run=dry_run)
    
    async def rollback_to_date(self, date: datetime, dry_run: bool = False) -> int:
        """Roll back migrations applied after the specified date"""
        applied = await self.get_applied_migrations()
        
        if not applied:
            logger.info("No migrations to roll back")
            return 0
        
        # Find target version based on date
        target_version = None
        date_version = date.strftime('%Y%m%d%H%M%S')
        
        for version in applied:
            if version <= date_version:
                target_version = version
            else:
                break
        
        if target_version:
            return await self.rollback(target=target_version, dry_run=dry_run)
        else:
            # Roll back everything
            return await self.rollback_all(dry_run=dry_run)
    
    async def redo(self, steps: int = 1) -> Tuple[int, int]:
        """
        Redo migrations (rollback then reapply)
        
        Returns:
            Tuple of (rolled_back_count, reapplied_count)
        """
        await self.initialize()
        
        # Get migrations to redo
        to_redo = await self.get_migrations_to_rollback(steps=steps)
        
        if not to_redo:
            logger.info("No migrations to redo")
            return 0, 0
        
        # Store versions to reapply
        versions_to_reapply = [v for v, _ in reversed(to_redo)]
        
        # Roll back
        logger.info(f"Rolling back {len(to_redo)} migration(s)...")
        rolled_back = await self.rollback(steps=steps)
        
        # Reapply
        logger.info(f"Reapplying {len(versions_to_reapply)} migration(s)...")
        reapplied = 0
        
        for version in versions_to_reapply:
            filepath = self.get_migration_file_by_version(version)
            if not filepath:
                logger.error(f"Cannot reapply {version}: file not found")
                continue
            
            up_sql, _ = self.parse_migration_file(filepath)
            
            if up_sql:
                try:
                    await self.db.execute_sql(up_sql)
                    await self.db.record_migration(version)
                    reapplied += 1
                    logger.info(f"✓ Reapplied {filepath.name}")
                except Exception as e:
                    logger.error(f"✗ Failed to reapply {filepath.name}: {e}")
                    raise
        
        return rolled_back, reapplied
    
    async def up(self, target: Optional[str] = None) -> int:
        """Run pending migrations up to target version"""
        await self.initialize()
        
        pending = await self.get_pending_migrations()
        if not pending:
            logger.info("No pending migrations")
            return 0
        
        applied_count = 0
        for version, filepath in pending:
            if target and version > target:
                break
            
            logger.info(f"Applying migration: {filepath.name}")
            up_sql, _ = self.parse_migration_file(filepath)
            
            if up_sql:
                try:
                    await self.db.execute_sql(up_sql)
                    await self.db.record_migration(version)
                    applied_count += 1
                    logger.info(f"✓ Applied {filepath.name}")
                except Exception as e:
                    logger.error(f"✗ Failed to apply {filepath.name}: {e}")
                    raise
            else:
                logger.warning(f"⚠ Skipping empty migration: {filepath.name}")
        
        return applied_count
    
    async def get_pending_migrations(self) -> List[Tuple[str, Path]]:
        """Get list of pending migrations"""
        applied = await self.db.get_applied_migrations()
        applied_set = set(applied)
        
        pending = []
        for filepath in self.get_migration_files():
            version = filepath.stem.split('_')[0]
            if version not in applied_set:
                pending.append((version, filepath))
        
        return pending
    
    async def status(self) -> dict:
        """Get migration status"""
        await self.initialize()
        
        applied = await self.db.get_applied_migrations()
        applied_set = set(applied)
        
        all_migrations = []
        for filepath in self.get_migration_files():
            version = filepath.stem.split('_')[0]
            
            # Check if migration has down SQL
            _, down_sql = self.parse_migration_file(filepath)
            has_down = bool(down_sql)
            
            all_migrations.append({
                'version': version,
                'name': filepath.name,
                'status': 'applied' if version in applied_set else 'pending',
                'reversible': has_down
            })
        
        return {
            'total': len(all_migrations),
            'applied': len(applied),
            'pending': len(all_migrations) - len(applied),
            'migrations': all_migrations
        }
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        await self.db.close()