"""
CREATESONLINE Database Migrations

Automatic database migrations using Alembic (SQLAlchemy's migration tool).
Provides Django-like migration workflow for CREATESONLINE applications.

Commands:
    createsonline-admin init-migrations        # Initialize migrations (once)
    createsonline-admin makemigrations "msg"   # Generate migration
    createsonline-admin migrate                # Apply migrations
    createsonline-admin migrate-history        # View history
    createsonline-admin migrate-downgrade -1   # Rollback
"""

import os
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging
from pathlib import Path

try:
    from alembic import command
    from alembic.config import Config
    from alembic.script import ScriptDirectory
    from alembic.runtime.migration import MigrationContext
    from sqlalchemy import create_engine, pool
    ALEMBIC_AVAILABLE = True
except ImportError:
    ALEMBIC_AVAILABLE = False
    print("⚠️  Alembic not installed. Run: pip install alembic")

# Setup logger
logger = logging.getLogger(__name__)



class AlembicMigrationManager:
    """
    Alembic-based migration manager for CREATESONLINE
    
    Provides Django-like migration workflow using Alembic under the hood.
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize migration manager
        
        Args:
            project_root: Project root directory (defaults to current directory)
        """
        if not ALEMBIC_AVAILABLE:
            raise ImportError("Alembic is required for migrations. Run: pip install alembic")
        
        self.project_root = project_root or Path.cwd()
        self.migrations_dir = self.project_root / "migrations"
        self.alembic_ini = self.project_root / "alembic.ini"
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///./createsonline.db')
    
    def init_migrations(self) -> bool:
        """
        Initialize Alembic migrations directory - FULLY AUTOMATIC
        
        Creates:
        - migrations/ directory structure
        - alembic.ini configuration
        - env.py with auto model detection
        - manage.py for easy commands
        
        Returns:
            True if successful
        """
        print("🔧 Initializing CREATESONLINE migrations...")
        
        try:
            # Check if already initialized
            if self.migrations_dir.exists():
                print(f"⚠️  Migrations directory already exists: {self.migrations_dir}")
                return False
            
            # Step 1: Create alembic.ini FIRST
            print(f"Creating {self.alembic_ini.name} ... ", end="", flush=True)
            self._create_alembic_ini()
            print("✅")
            
            # Step 2: Initialize Alembic structure
            print(f"Creating directory {self.migrations_dir} ... ", end="", flush=True)
            alembic_cfg = Config(str(self.alembic_ini))
            alembic_cfg.set_main_option("script_location", str(self.migrations_dir))
            alembic_cfg.set_main_option("sqlalchemy.url", self.database_url)
            command.init(alembic_cfg, str(self.migrations_dir))
            print("✅")
            
            # Step 3: Customize env.py for auto model detection
            print("Customizing env.py for CREATESONLINE ... ", end="", flush=True)
            self._customize_env_py()
            print("✅")
            
            # Step 4: Create manage.py for easy commands
            print("Creating manage.py ... ", end="", flush=True)
            self._create_manage_py()
            print("✅")
            
            print(f"\n✅ Migrations initialized successfully!")
            print(f"📁 Migrations: {self.migrations_dir}")
            print(f"⚙️  Config: {self.alembic_ini}")
            print(f"🔧 Commands: manage.py")
            print("\n📝 Next steps:")
            print("   1. Define your models in models.py")
            print("   2. Run: python manage.py makemigrations 'Initial migration'")
            print("   3. Run: python manage.py migrate")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error initializing migrations:")
            import traceback
            traceback.print_exc()
            return False
    
    def create_migration(self, message: str = "auto") -> bool:
        """
        Auto-generate migration from model changes
        
        Args:
            message: Migration description
        
        Returns:
            True if migration created
        """
        print(f"🔍 Detecting model changes...")
        
        try:
            alembic_cfg = self._get_alembic_config()
            
            # Auto-generate migration
            command.revision(
                alembic_cfg,
                message=message,
                autogenerate=True
            )
            
            print(f"✅ Migration created: {message}")
            print("📝 Next step: Run 'createsonline-admin migrate' to apply")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating migration: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def apply_migrations(self, revision: str = "head") -> bool:
        """
        Apply pending migrations to database
        
        Args:
            revision: Target revision (default: 'head' for latest)
        
        Returns:
            True if successful
        """
        print(f"🚀 Applying migrations to: {self.database_url}")
        
        try:
            alembic_cfg = self._get_alembic_config()
            
            # Upgrade to target revision
            command.upgrade(alembic_cfg, revision)
            
            print("✅ Migrations applied successfully!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error applying migrations: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def downgrade_migration(self, steps: int = 1) -> bool:
        """
        Rollback migrations
        
        Args:
            steps: Number of migrations to rollback (default: 1)
        
        Returns:
            True if successful
        """
        print(f"⏪ Rolling back {steps} migration(s)...")
        
        try:
            alembic_cfg = self._get_alembic_config()
            
            # Downgrade
            revision = f"-{steps}"
            command.downgrade(alembic_cfg, revision)
            
            print(f"✅ Rolled back {steps} migration(s)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error rolling back: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def show_history(self) -> bool:
        """
        Show migration history
        
        Returns:
            True if successful
        """
        print("📜 Migration History:")
        print("=" * 60)
        
        try:
            alembic_cfg = self._get_alembic_config()
            
            # Show history
            command.history(alembic_cfg, verbose=True)
            
            return True
            
        except Exception as e:
            print(f"❌ Error showing history: {e}")
            return False
    
    def show_current(self) -> bool:
        """
        Show current migration revision
        
        Returns:
            True if successful
        """
        print("📍 Current Revision:")
        print("=" * 60)
        
        try:
            alembic_cfg = self._get_alembic_config()
            
            # Show current revision
            command.current(alembic_cfg, verbose=True)
            
            return True
            
        except Exception as e:
            print(f"❌ Error showing current revision: {e}")
            return False
    
    def show_pending(self) -> bool:
        """
        Show pending migrations
        
        Returns:
            True if successful
        """
        print("⏳ Pending Migrations:")
        print("=" * 60)
        
        try:
            # Get current and head revisions
            engine = create_engine(self.database_url, poolclass=pool.NullPool)
            
            with engine.connect() as connection:
                context = MigrationContext.configure(connection)
                current = context.get_current_revision()
            
            alembic_cfg = self._get_alembic_config()
            script = ScriptDirectory.from_config(alembic_cfg)
            head = script.get_current_head()
            
            if current == head:
                print("✅ No pending migrations - database is up to date")
            else:
                print(f"Current: {current or 'None'}")
                print(f"Latest:  {head}")
                print("\n⚠️  Pending migrations detected!")
                print("Run: createsonline-admin migrate")
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking pending migrations: {e}")
            return False
    
    def _get_alembic_config(self) -> Config:
        """Get Alembic configuration"""
        if not self.alembic_ini.exists():
            raise FileNotFoundError(
                f"Alembic not initialized. Run: createsonline-admin init-migrations"
            )
        
        alembic_cfg = Config(str(self.alembic_ini))
        alembic_cfg.set_main_option("script_location", str(self.migrations_dir))
        alembic_cfg.set_main_option("sqlalchemy.url", self.database_url)
        return alembic_cfg
    
    def _create_alembic_ini(self):
        """Create alembic.ini configuration file"""
        alembic_ini_content = f'''# Alembic Configuration for CREATESONLINE
# Auto-generated - DO NOT edit manually

[alembic]
script_location = migrations
sqlalchemy.url = {self.database_url}

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
'''
        self.alembic_ini.write_text(alembic_ini_content)
    
    def _create_manage_py(self):
        """Create manage.py file for easy migration commands"""
        manage_py_path = self.project_root / "manage.py"
        
        # Don't overwrite if exists
        if manage_py_path.exists():
            return
        
        manage_py_content = '''#!/usr/bin/env python
"""
Database Migration Management

Auto-generated by CREATESONLINE
This file provides easy access to migration commands.
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import models - ADD YOUR MODELS HERE
try:
    from models import *  # Import all models
except ImportError:
    print("WARNING: models.py not found. Create models.py with your database models.")

# Import migration functions
from createsonline.database.migrations import (
    init_migrations, make_migrations, migrate, migrate_downgrade,
    migrate_history, migrate_current, migrate_pending
)

def print_help():
    print("CREATESONLINE Migration Management")
    print("=" * 60)
    print("Usage: python manage.py <command> [options]")
    print("")
    print("Commands:")
    print("  init-migrations              Initialize migration system (one-time)")
    print("  makemigrations <message>     Generate new migration from model changes")
    print("  migrate                      Apply pending migrations to database")
    print("  migrate-history              Show migration history")
    print("  migrate-current              Show current database version")
    print("  migrate-pending              Check for pending migrations")
    print("  migrate-downgrade <steps>    Rollback migrations (default: 1)")
    print("")
    print("Examples:")
    print("  python manage.py makemigrations 'Add User model'")
    print("  python manage.py migrate")
    print("  python manage.py migrate-downgrade -1")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == 'init-migrations':
            init_migrations()
        elif command == 'makemigrations':
            message = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else 'Auto migration'
            make_migrations(message)
        elif command == 'migrate':
            migrate()
        elif command == 'migrate-history':
            migrate_history()
        elif command == 'migrate-current':
            migrate_current()
        elif command == 'migrate-pending':
            migrate_pending()
        elif command == 'migrate-downgrade':
            steps = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            migrate_downgrade(steps)
        else:
            print(f"ERROR: Unknown command: {command}")
            print("")
            print_help()
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
'''
        manage_py_path.write_text(manage_py_content, encoding='utf-8')
    
    def _customize_env_py(self):
        """Customize env.py for CREATESONLINE"""
        env_py_path = self.migrations_dir / "env.py"
        
        env_py_content = '''# migrations/env.py
"""
CREATESONLINE Alembic Environment Configuration

This file is automatically configured to work with CREATESONLINE models.
"""

from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import CREATESONLINE database components
try:
    from createsonline.database.models import CreatesonlineModel
except ImportError:
    print("Warning: CREATESONLINE not found in path")
    CreatesonlineModel = None

# Import your application models
try:
    import sys
    from pathlib import Path
    
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Try to import models
    try:
        from models import *  # Import all your models
    except ImportError:
        print("Warning: Could not import models.py - make sure it exists")
except Exception as e:
    print(f"Warning: Error importing models: {e}")

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get metadata from CREATESONLINE base model
if CreatesonlineModel is not None:
    target_metadata = CreatesonlineModel.metadata
else:
    target_metadata = None

# Get database URL from environment
database_url = os.getenv('DATABASE_URL', config.get_main_option("sqlalchemy.url"))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = database_url
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
        
        with open(env_py_path, 'w', encoding='utf-8') as f:
            f.write(env_py_content)
    
    def _customize_alembic_ini(self):
        """Customize alembic.ini (not needed - created fresh)"""
        pass


# Legacy migration classes (kept for backward compatibility)
class Migration:
    """
    Represents a single database migration.
    """
    
    def __init__(self, name: str, description: str = "", version: str = ""):
        self.name = name
        self.description = description
        self.version = version
        self.timestamp = datetime.now()
        self.applied = False
    
    def up(self):
        """Apply this migration"""
        raise NotImplementedError("Subclasses must implement up() method")
    
    def down(self):
        """Reverse this migration"""
        raise NotImplementedError("Subclasses must implement down() method")


class MigrationManager:
    """
    Legacy migration manager (now uses Alembic under the hood)
    Kept for backward compatibility
    """
    
    def __init__(self, migrations_dir: str = "migrations", project_root: Optional[Path] = None):
        """Initialize using Alembic backend"""
        if ALEMBIC_AVAILABLE:
            self.alembic_manager = AlembicMigrationManager(project_root)
        else:
            # Fallback to simple file-based tracking
            self.migrations_dir = Path(migrations_dir)
            self.migrations_dir.mkdir(exist_ok=True)
            self.applied_migrations_file = self.migrations_dir / "applied.json"
            self.migrations: List[Migration] = []
            self.applied_migrations = self._load_applied_migrations()
    
    def _load_applied_migrations(self) -> List[str]:
        """Load list of applied migrations"""
        if self.applied_migrations_file.exists():
            try:
                with open(self.applied_migrations_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def _save_applied_migrations(self):
        """Save list of applied migrations"""
        try:
            with open(self.applied_migrations_file, 'w') as f:
                json.dump(self.applied_migrations, f, indent=2)
        except IOError as e:
            logger.warning(f"Could not save applied migrations: {e}")
    
    def add_migration(self, migration: Migration):
        """Add a migration to the manager"""
        self.migrations.append(migration)
    
    def apply_migrations(self):
        """Apply all pending migrations"""
        applied_count = 0
        pending_migrations = [m for m in self.migrations if m.name not in self.applied_migrations]
        
        if not pending_migrations:
            logger.info("No pending migrations to apply")
            return
        
        logger.info(f"Applying {len(pending_migrations)} pending migrations...")
        
        for migration in pending_migrations:
            logger.info(f"Applying migration: {migration.name}")
            try:
                migration.up()
                self.applied_migrations.append(migration.name)
                migration.applied = True
                applied_count += 1
                logger.info(f"âœ… Applied: {migration.name}")
            except Exception as e:
                logger.error(f"âŒ Failed to apply {migration.name}: {e}")
                break
        
        if applied_count > 0:
            self._save_applied_migrations()
            logger.info(f"Applied {applied_count} migrations successfully")
    
    def rollback_migration(self, migration_name: str):
        """Rollback a specific migration"""
        for migration in reversed(self.migrations):
            if migration.name == migration_name:
                if migration_name in self.applied_migrations:
                    logger.info(f"Rolling back migration: {migration_name}")
                    try:
                        migration.down()
                        self.applied_migrations.remove(migration_name)
                        migration.applied = False
                        self._save_applied_migrations()
                        logger.info(f"âœ… Rolled back: {migration_name}")
                    except Exception as e:
                        logger.error(f"âŒ Failed to rollback {migration_name}: {e}")
                else:
                    logger.warning(f"Migration {migration_name} is not applied")
                return
        
        logger.error(f"Migration {migration_name} not found")
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get status of all migrations"""
        return {
            "total_migrations": len(self.migrations),
            "applied_migrations": len(self.applied_migrations),
            "pending_migrations": len(self.migrations) - len(self.applied_migrations),
            "migrations": [
                {
                    "name": m.name,
                    "description": m.description,
                    "applied": m.name in self.applied_migrations,
                    "timestamp": m.timestamp.isoformat() if hasattr(m, 'timestamp') else None
                }
                for m in self.migrations
            ]
        }

# Convenience functions for CLI
def init_migrations(project_root: Optional[Path] = None) -> bool:
    """Initialize migrations for a project"""
    if not ALEMBIC_AVAILABLE:
        print("❌ Alembic not installed. Run: pip install alembic")
        return False
    manager = AlembicMigrationManager(project_root)
    return manager.init_migrations()


def make_migrations(message: str = "auto", project_root: Optional[Path] = None) -> bool:
    """Create a new migration"""
    if not ALEMBIC_AVAILABLE:
        print("❌ Alembic not installed. Run: pip install alembic")
        return False
    manager = AlembicMigrationManager(project_root)
    return manager.create_migration(message)


def migrate(revision: str = "head", project_root: Optional[Path] = None) -> bool:
    """Apply migrations"""
    if not ALEMBIC_AVAILABLE:
        print("❌ Alembic not installed. Run: pip install alembic")
        return False
    manager = AlembicMigrationManager(project_root)
    return manager.apply_migrations(revision)


def migrate_downgrade(steps: int = 1, project_root: Optional[Path] = None) -> bool:
    """Rollback migrations"""
    if not ALEMBIC_AVAILABLE:
        print("❌ Alembic not installed. Run: pip install alembic")
        return False
    manager = AlembicMigrationManager(project_root)
    return manager.downgrade_migration(steps)


def migrate_history(project_root: Optional[Path] = None) -> bool:
    """Show migration history"""
    if not ALEMBIC_AVAILABLE:
        print("❌ Alembic not installed. Run: pip install alembic")
        return False
    manager = AlembicMigrationManager(project_root)
    return manager.show_history()


def migrate_current(project_root: Optional[Path] = None) -> bool:
    """Show current revision"""
    if not ALEMBIC_AVAILABLE:
        print("❌ Alembic not installed. Run: pip install alembic")
        return False
    manager = AlembicMigrationManager(project_root)
    return manager.show_current()


def migrate_pending(project_root: Optional[Path] = None) -> bool:
    """Show pending migrations"""
    if not ALEMBIC_AVAILABLE:
        print("❌ Alembic not installed. Run: pip install alembic")
        return False
    manager = AlembicMigrationManager(project_root)
    return manager.show_pending()