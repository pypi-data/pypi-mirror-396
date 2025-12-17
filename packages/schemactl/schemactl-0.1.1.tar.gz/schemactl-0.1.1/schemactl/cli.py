import asyncio
import click
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from schemactl.config import DatabaseConfig
from schemactl.services import MigrationService



console = Console()
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def get_config() -> DatabaseConfig:
    """Load configuration from environment or config file"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    return DatabaseConfig(
        url=os.getenv('DATABASE_URL', 'postgresql+asyncpg://localhost/mydb'),
        migrations_dir=Path(os.getenv('MIGRATIONS_DIR', './migrations')),
        schema_file=Path(os.getenv('SCHEMA_FILE', './schema.sql')),
        schema_table=os.getenv('SCHEMA_TABLE', 'schema_migrations'),
        echo=os.getenv('DB_ECHO', '').lower() == 'true'
    )


@click.group()
@click.option('--debug', is_flag=True, help='Enable debug output')
@click.pass_context
def cli(ctx, debug):
    """Framework-agnostic database migration tool"""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    ctx.obj = get_config()

@cli.command()
@click.option('--message', default="", help='Migration name')
@click.option('--auto', is_flag=True, help='Auto-generate from models')
@click.option('--models', help='Python module path to models (e.g., app.models)')
@click.option('--models-file', help='Path to models file')
@click.option('--show-excluded', is_flag=True, help='Show excluded tables')
@click.pass_obj
def new(config: DatabaseConfig, message: str, auto: bool, models: Optional[str], models_file: Optional[str], show_excluded: bool):
    """Generate a new migration file"""
    
    # Update config if models path provided
    if models:
        config.models_path = models
    if models_file:
        config.models_file = Path(models_file)
    
    async def run():
        service = MigrationService(config)

        if show_excluded:
            console.print("\n[yellow]Excluded tables:[/yellow]")
            console.print(f"  Exact matches: {', '.join(sorted(config.exclude_tables))}")
            if config.exclude_patterns:
                console.print(f"  Patterns: {', '.join(config.exclude_patterns)}")
            console.print()        
        
        if auto:
            # Auto-generate migration from models
            console.print("[yellow]Loading models and comparing with database...[/yellow]")
            
            try:
                version, up_sql, down_sql = service.alembic.generate_migration(message)
                
                if not up_sql and not down_sql:
                    console.print("[yellow]No changes detected[/yellow]")
                    return
                
                # Create migration file with generated SQL
                filename = f"{version}_{service.sanitize_name(message)}.sql"
                filepath = config.migrations_dir / filename
                
                content = f"""-- migrate:up
-- Auto-generated migration: {message}
{up_sql}

-- migrate:down
-- Rollback: {message}
{down_sql}
"""
                filepath.write_text(content)
                console.print(f"[green]✓[/green] Generated migration: [cyan]{filepath}[/cyan]")
                
            except Exception as e:
                console.print(f"[red]Failed to generate migration: {e}[/red]")
                raise
        else:
            # Create empty migration template
            filepath = await service.new_migration(message)
            console.print(f"[green]✓[/green] Created migration: [cyan]{filepath}[/cyan]")
        
        await service.cleanup()
    
    asyncio.run(run())


@cli.command()
@click.option('--target', help='Migrate up to specific version')
@click.option('--dry-run', is_flag=True, help='Show what would be done')
@click.pass_obj
def up(config: DatabaseConfig, target: Optional[str], dry_run: bool):
    """Create database and run pending migrations"""
    async def run():
        service = MigrationService(config)
        
        # Create database if needed
        console.print("[yellow]Ensuring database exists...[/yellow]")
        await service.db.create_database()
        
        if dry_run:
            console.print("\n[yellow]Pending migrations:[/yellow]")
            pending = await service.get_pending_migrations()
            for version, filepath in pending:
                if target and version > target:
                    break
                console.print(f"  • {filepath.name}")
            console.print(f"\n[yellow]Would apply {len(pending)} migration(s)[/yellow]")
        else:
            console.print("[yellow]Running migrations...[/yellow]")
            count = await service.up(target)
            console.print(f"[green]✓[/green] Applied {count} migration(s)")
        
        await service.cleanup()
    
    asyncio.run(run())    


@cli.command()
@click.option('--steps', '-n', default=1, help='Number of migrations to roll back')
@click.option('--target', '-t', help='Roll back to specific version')
@click.option('--all', 'rollback_all', is_flag=True, help='Roll back all migrations')
@click.option('--date', help='Roll back to date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)')
@click.option('--dry-run', is_flag=True, help='Show what would be rolled back')
@click.option('--force', '-f', is_flag=True, help='Skip confirmation')
@click.pass_obj
def rollback(
    config: DatabaseConfig, 
    steps: int, 
    target: Optional[str],
    rollback_all: bool,
    date: Optional[str],
    dry_run: bool,
    force: bool
):
    """Roll back the most recent migration(s)"""
    
    async def run():
        service = MigrationService(config)
        
        # Determine what to rollback
        if rollback_all:
            if not force and not dry_run:
                if not Confirm.ask("[red]Roll back ALL migrations?[/red]"):
                    console.print("[yellow]Aborted[/yellow]")
                    return
            
            console.print("[yellow]Rolling back all migrations...[/yellow]")
            count = await service.rollback_all(dry_run=dry_run)
            
        elif date:
            # Parse date
            try:
                if len(date) == 10:  # Just date
                    dt = datetime.strptime(date, '%Y-%m-%d')
                else:  # Date and time
                    dt = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                console.print("[red]Invalid date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS[/red]")
                return
            
            console.print(f"[yellow]Rolling back to {dt}...[/yellow]")
            count = await service.rollback_to_date(dt, dry_run=dry_run)
            
        elif target:
            console.print(f"[yellow]Rolling back to version {target}...[/yellow]")
            count = await service.rollback(target=target, dry_run=dry_run)
            
        else:
            # Roll back by steps
            if not force and not dry_run and steps > 1:
                if not Confirm.ask(f"[yellow]Roll back {steps} migrations?[/yellow]"):
                    console.print("[yellow]Aborted[/yellow]")
                    return
            
            console.print(f"[yellow]Rolling back {steps} migration(s)...[/yellow]")
            count = await service.rollback(steps=steps, dry_run=dry_run)
        
        if dry_run:
            console.print(f"[yellow]Would roll back {count} migration(s)[/yellow]")
        else:
            console.print(f"[green]✓[/green] Rolled back {count} migration(s)")
        
        await service.cleanup()
    
    asyncio.run(run())    


@cli.command()
@click.option('--steps', '-n', default=1, help='Number of migrations to roll back')
@click.option('--target', '-t', help='Roll back to specific version')
@click.option('--all', 'rollback_all', is_flag=True, help='Roll back all migrations')
@click.option('--dry-run', is_flag=True, help='Show what would be done')
@click.option('--force', '-f', is_flag=True, help='Skip confirmation')
@click.pass_obj
def down(
    config: DatabaseConfig,
    steps: int,
    target: Optional[str],
    rollback_all: bool,
    dry_run: bool,
    force: bool
):
    """Alias for rollback - roll back migration(s)"""
    # Call rollback with same parameters
    ctx = click.get_current_context()
    ctx.invoke(
        rollback,
        steps=steps,
        target=target,
        rollback_all=rollback_all,
        date=None,
        dry_run=dry_run,
        force=force
    )    


@cli.command()
@click.option('--steps', '-n', default=1, help='Number of migrations to redo')
@click.option('--dry-run', is_flag=True, help='Show what would be done')
@click.pass_obj
def redo(config: DatabaseConfig, steps: int, dry_run: bool):
    """Roll back and reapply migration(s)"""
    
    async def run():
        service = MigrationService(config)
        
        if dry_run:
            # Show what would be redone
            to_redo = await service.get_migrations_to_rollback(steps=steps)
            console.print(f"[yellow]Would redo {len(to_redo)} migration(s):[/yellow]")
            for version, filepath in to_redo:
                console.print(f"  • {filepath.name}")
        else:
            console.print(f"[yellow]Redoing {steps} migration(s)...[/yellow]")
            rolled_back, reapplied = await service.redo(steps=steps)
            console.print(f"[green]✓[/green] Rolled back {rolled_back}, reapplied {reapplied}")
        
        await service.cleanup()
    
    asyncio.run(run())    


@cli.command()
@click.argument('version')
@click.pass_obj
def goto(config: DatabaseConfig, version: str):
    """Migrate to a specific version (up or down)"""
    
    async def run():
        service = MigrationService(config)
        await service.initialize()
        
        # Get current state
        applied = await service.get_applied_migrations()
        
        if version in applied:
            # Need to rollback
            console.print(f"[yellow]Rolling back to version {version}...[/yellow]")
            count = await service.rollback(target=version)
            console.print(f"[green]✓[/green] Rolled back {count} migration(s)")
        else:
            # Need to migrate up
            console.print(f"[yellow]Migrating up to version {version}...[/yellow]")
            count = await service.up(target=version)
            console.print(f"[green]✓[/green] Applied {count} migration(s)")
        
        await service.cleanup()
    
    asyncio.run(run())    


@cli.command()
@click.argument('version')
@click.pass_obj
def show(config: DatabaseConfig, version: str):
    """Show the SQL for a specific migration"""
    
    async def run():
        service = MigrationService(config)
        
        # Find migration file
        filepath = service.get_migration_file_by_version(version)
        
        if not filepath:
            console.print(f"[red]Migration {version} not found[/red]")
            return
        
        # Parse and display
        up_sql, down_sql = service.parse_migration_file(filepath)
        
        console.print(f"\n[cyan]Migration: {filepath.name}[/cyan]\n")
        
        console.print("[green]-- UP Migration --[/green]")
        if up_sql:
            console.print(up_sql)
        else:
            console.print("[yellow]No UP migration[/yellow]")
        
        console.print("\n[red]-- DOWN Migration --[/red]")
        if down_sql:
            console.print(down_sql)
        else:
            console.print("[yellow]No DOWN migration[/yellow]")
        
        await service.cleanup()
    
    asyncio.run(run())    


@cli.command()
@click.option('--exit-code', is_flag=True, help='Exit with non-zero if pending migrations')
@click.option('--quiet', is_flag=True, help='Suppress output')
@click.pass_obj
def status(config: DatabaseConfig, exit_code: bool, quiet: bool):
    """Show the status of all migrations"""
    async def run():
        service = MigrationService(config)
        status_info = await service.status()
        
        if not quiet:
            table = Table(title="Migration Status")
            table.add_column("Version", style="cyan")
            table.add_column("Name", style="white")
            table.add_column("Status", style="green")
            
            for migration in status_info['migrations']:
                status_style = "green" if migration['status'] == 'applied' else "yellow"
                table.add_row(
                    migration['version'],
                    migration['name'],
                    f"[{status_style}]{migration['status']}[/{status_style}]"
                )
            
            console.print(table)
            console.print(f"\nTotal: {status_info['total']} | Applied: {status_info['applied']} | Pending: {status_info['pending']}")
        
        await service.cleanup()
        
        if exit_code and status_info['pending'] > 0:
            exit(1)
    
    asyncio.run(run())    


@cli.command()
@click.option('--check-excluded', is_flag=True, help='Check which tables would be excluded')
@click.pass_obj
def info(config: DatabaseConfig, check_excluded: bool):
    """Show migration configuration and exclusions"""
    
    async def run():
        service = MigrationService(config)
        
        # Show configuration
        console.print("\n[cyan]Migration Configuration[/cyan]")
        console.print(f"  Database URL: {config.url.split('@')[-1]}")  # Hide credentials
        console.print(f"  Migrations dir: {config.migrations_dir}")
        console.print(f"  Schema table: {config.schema_table}")
        console.print(f"  Models path: {config.models_path or 'auto-discover'}")
        
        console.print("\n[yellow]Exclusions[/yellow]")
        console.print(f"  Always excluded: {config.schema_table}")
        
        if config.exclude_tables:
            console.print(f"  User excluded: {', '.join(sorted(config.exclude_tables - {config.schema_table}))}")
        
        if config.exclude_patterns:
            console.print(f"  Patterns: {', '.join(config.exclude_patterns)}")
        
        if check_excluded:
            # Check what tables exist and would be excluded
            console.print("\n[yellow]Checking database tables...[/yellow]")
            
            from sqlalchemy import inspect
            
            with service.db.sync_engine.connect() as conn:
                inspector = inspect(conn)
                all_tables = inspector.get_table_names()
                
                excluded = []
                included = []
                
                for table in all_tables:
                    if config.should_exclude_table(table):
                        excluded.append(table)
                    else:
                        included.append(table)
                
                if excluded:
                    console.print("\n[red]Excluded tables:[/red]")
                    for table in sorted(excluded):
                        console.print(f"  ✗ {table}")
                
                if included:
                    console.print("\n[green]Included tables:[/green]")
                    for table in sorted(included):
                        console.print(f"  ✓ {table}")
        
        await service.cleanup()
    
    asyncio.run(run())    