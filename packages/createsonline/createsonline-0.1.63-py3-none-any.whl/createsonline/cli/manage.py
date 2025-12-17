#!/usr/bin/env python
"""
CREATESONLINE Management CLI

Database and admin management commands.
For project creation and server, use: createsonline "create project" or createsonline "start server"
"""
import sys
import os
import logging

logger = logging.getLogger("createsonline.cli.manage")


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1]
    
    # Legacy database commands
    if command == "migrate":
        migrate_database()
    elif command == "createsuperuser":
        create_superuser()
    elif command == "initdb":
        init_database()
    
    # New Alembic migration commands
    elif command == "init-migrations":
        init_migrations_cmd()
    elif command == "makemigrations":
        make_migrations_cmd()
    elif command == "apply-migrations":
        apply_migrations_cmd()
    elif command == "migrate-history":
        migrate_history_cmd()
    elif command == "migrate-current":
        migrate_current_cmd()
    elif command == "migrate-pending":
        migrate_pending_cmd()
    elif command == "migrate-downgrade":
        migrate_downgrade_cmd()
    
    # Other commands
    elif command == "shell":
        open_shell()
    elif command == "collectstatic":
        collect_static()
    elif command == "help":
        print_help()
    else:
        logger.info(f"Error: Unknown command: {command}")
        print_help()


def print_help():
    """Print help message"""
    logger.info("""
CREATESONLINE Management Commands

Usage: createsonline-admin <command>

Database Commands (Legacy):
    migrate              Create/update database tables (simple mode)
    initdb               Initialize database with tables and default data
    createsuperuser      Create a superuser account

Migration Commands (Alembic - Recommended):
    init-migrations                Initialize migrations (once per project)
    makemigrations "message"       Generate migration from model changes
    apply-migrations               Apply pending migrations to database
    migrate-history                Show migration history
    migrate-current                Show current migration version
    migrate-pending                Show pending migrations
    migrate-downgrade -1           Rollback last migration

Other Commands:
    shell                Open Python shell with app context
    collectstatic        Collect static files from framework to project
    help                 Show this help message

Examples:
    # Setup migrations (first time)
    createsonline-admin init-migrations
    
    # After changing models
    createsonline-admin makemigrations "Added price field"
    createsonline-admin apply-migrations
    
    # Check migration status
    createsonline-admin migrate-pending
    createsonline-admin migrate-history
    
    # Rollback if needed
    createsonline-admin migrate-downgrade -1
    
    # Legacy commands
    createsonline-admin createsuperuser
    createsonline-admin initdb

Note: For project creation and server commands, use the natural language CLI:
    createsonline "create project myapp"
    createsonline "start development server"
""")


def migrate_database():
    """Create/update database tables"""
    logger.info("Running migrations...")
    
    try:
        from sqlalchemy import create_engine
        from createsonline.auth.models import Base as AuthBase
        
        database_url = os.getenv("DATABASE_URL", "sqlite:///./createsonline.db")
        logger.info(f"Database: {database_url}")
        
        engine = create_engine(database_url, echo=False)
        
        logger.info("Creating tables...")
        try:
            from createsonline.admin import content
        except:
            pass
        
        AuthBase.metadata.create_all(engine)
        
        logger.info("Migrations completed successfully!")
        logger.info(f"Database: {database_url.replace('sqlite:///./', '')}")
        
    except Exception as e:
        logger.info(f"Error: Migration failed: {e}")
        import traceback
        traceback.print_exc()


def create_superuser():
    """Create a superuser"""
    logger.info("Create Superuser")
    logger.info("=" * 50)
    
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from createsonline.auth.models import User, create_superuser as create_su
        
        database_url = os.getenv("DATABASE_URL", "sqlite:///./createsonline.db")
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        try:
            # Get username
            while True:
                username = input("Username: ").strip()
                if not username:
                    logger.info("Error: Username cannot be empty")
                    continue
                
                existing = session.query(User).filter_by(username=username).first()
                if existing:
                    logger.info(f"Error: User '{username}' already exists")
                    continue
                
                break
            
            # Get email
            while True:
                email = input("Email address: ").strip()
                if not email:
                    logger.info("Error: Email cannot be empty")
                    continue
                
                if '@' not in email:
                    logger.info("Error: Invalid email format")
                    continue
                
                break
            
            # Get password
            import getpass
            while True:
                password = getpass.getpass("Password: ")
                if not password:
                    logger.info("Error: Password cannot be empty")
                    continue
                
                if len(password) < 8:
                    logger.info("Error: Password must be at least 8 characters")
                    continue
                
                password_confirm = getpass.getpass("Password (again): ")
                if password != password_confirm:
                    logger.info("Error: Passwords don't match")
                    continue
                
                break
            
            # Create superuser
            user = create_su(
                username=username,
                email=email,
                password=password
            )
            
            session.add(user)
            session.commit()
            
            logger.info("\nSuperuser created successfully!")
            logger.info(f"Username: {username}")
            logger.info(f"Email: {email}")
            logger.info(f"\nYou can now login at: http://localhost:8000/admin")
            
        except KeyboardInterrupt:
            logger.info("\nOperation cancelled")
        except Exception as e:
            session.rollback()
            logger.info(f"\nError: {e}")
        finally:
            session.close()
            
    except ImportError as e:
        logger.info(f"Error: Missing dependency: {e}")
        logger.info("Install SQLAlchemy: pip install sqlalchemy")
    except Exception as e:
        logger.info(f"Error: {e}")


def init_database():
    """Initialize database with tables and default data"""
    logger.info("Initializing CREATESONLINE database...")
    logger.info("=" * 50)
    
    # Run migrations first
    migrate_database()
    
    # Create default permissions
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from createsonline.auth.models import Permission, create_default_permissions
        
        database_url = os.getenv("DATABASE_URL", "sqlite:///./createsonline.db")
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        try:
            logger.info("\nCreating default permissions...")
            permissions = create_default_permissions()
            
            for perm in permissions:
                existing = session.query(Permission).filter_by(
                    codename=perm.codename,
                    content_type=perm.content_type
                ).first()
                
                if not existing:
                    session.add(perm)
                    logger.info(f"  Created: {perm.content_type}.{perm.codename}")
            
            session.commit()
            logger.info("Default permissions created")
            
        except Exception as e:
            session.rollback()
            logger.info(f"Warning: Could not create permissions: {e}")
        finally:
            session.close()
    
    except Exception as e:
        logger.info(f"Warning: Could not create permissions: {e}")
    
    # Prompt to create superuser
    logger.info("\n" + "=" * 50)
    response = input("Do you want to create a superuser now? [y/N] ").strip().lower()
    
    if response in ['y', 'yes']:
        create_superuser()
    else:
        logger.info("\nYou can create a superuser later with:")
        logger.info("   createsonline-admin createsuperuser")
    
    logger.info("\nDatabase initialization complete!")


def open_shell():
    """Open interactive Python shell"""
    logger.info("CREATESONLINE Interactive Shell")
    logger.info("=" * 50)
    
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from createsonline.auth.models import User, Group, Permission
        
        database_url = os.getenv("DATABASE_URL", "sqlite:///./createsonline.db")
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        logger.info("\nImported:")
        logger.info("  - User, Group, Permission from createsonline.auth.models")
        logger.info("  - session (SQLAlchemy session)")
        logger.info(f"\nDatabase: {database_url}")
        logger.info("\nExample:")
        logger.info("  users = session.query(User).all()")
        logger.info("  for user in users: print(user.username)")
        logger.info()
        
        import code
        code.interact(local=locals())
        
    except Exception as e:
        logger.info(f"Error: {e}")


def collect_static():
    """Collect static files from framework to project"""
    logger.info("Collecting static files...")
    logger.info("=" * 50)
    
    try:
        import shutil
        from pathlib import Path
        
        # Get framework static directory
        import createsonline
        framework_root = Path(createsonline.__file__).parent
        framework_static = framework_root / "static"
        
        # Get project static directory (current directory)
        project_static = Path.cwd() / "static"
        
        if not framework_static.exists():
            logger.info("No framework static files to collect")
            return
        
        # Create project static directory if it doesn't exist
        project_static.mkdir(exist_ok=True)
        
        # Copy files
        collected_count = 0
        skipped_count = 0
        
        for source_file in framework_static.rglob("*"):
            if source_file.is_file():
                # Calculate relative path
                rel_path = source_file.relative_to(framework_static)
                dest_file = project_static / rel_path
                
                # Create parent directories
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Check if file exists and is different
                if dest_file.exists():
                    # Compare file sizes as quick check
                    if dest_file.stat().st_size == source_file.stat().st_size:
                        skipped_count += 1
                        continue
                
                # Copy file
                shutil.copy2(source_file, dest_file)
                collected_count += 1
                logger.info(f"  Copied: {rel_path}")
        
        logger.info(f"\nCollected {collected_count} static file(s)")
        if skipped_count > 0:
            logger.info(f"Skipped {skipped_count} unchanged file(s)")
        
        logger.info(f"Static files location: {project_static.absolute()}")
        
    except ImportError:
        logger.info("Error: CREATESONLINE package not found")
    except Exception as e:
        logger.info(f"Error: {e}")
        import traceback
        traceback.print_exc()


# ========================================
# ALEMBIC MIGRATION COMMANDS
# ========================================

def init_migrations_cmd():
    """Initialize migrations directory"""
    logger.info("Initializing migrations...")
    
    try:
        from createsonline.database.migrations import init_migrations
        success = init_migrations()
        
        if not success:
            logger.info("Migration initialization failed or already exists")
    except Exception as e:
        logger.info(f"Error: {e}")
        import traceback
        traceback.print_exc()


def make_migrations_cmd():
    """Create a new migration"""
    logger.info("Generating migration...")
    
    # Get migration message from command line args
    message = "auto"
    if len(sys.argv) > 2:
        message = " ".join(sys.argv[2:])
    
    try:
        from createsonline.database.migrations import make_migrations
        success = make_migrations(message)
        
        if not success:
            logger.info("Migration generation failed")
    except Exception as e:
        logger.info(f"Error: {e}")
        import traceback
        traceback.print_exc()


def apply_migrations_cmd():
    """Apply pending migrations"""
    logger.info("Applying migrations...")
    
    try:
        from createsonline.database.migrations import migrate
        success = migrate()
        
        if not success:
            logger.info("Migration application failed")
    except Exception as e:
        logger.info(f"Error: {e}")
        import traceback
        traceback.print_exc()


def migrate_history_cmd():
    """Show migration history"""
    try:
        from createsonline.database.migrations import migrate_history
        migrate_history()
    except Exception as e:
        logger.info(f"Error: {e}")
        import traceback
        traceback.print_exc()


def migrate_current_cmd():
    """Show current migration version"""
    try:
        from createsonline.database.migrations import migrate_current
        migrate_current()
    except Exception as e:
        logger.info(f"Error: {e}")
        import traceback
        traceback.print_exc()


def migrate_pending_cmd():
    """Show pending migrations"""
    try:
        from createsonline.database.migrations import migrate_pending
        migrate_pending()
    except Exception as e:
        logger.info(f"Error: {e}")
        import traceback
        traceback.print_exc()


def migrate_downgrade_cmd():
    """Rollback migrations"""
    steps = 1
    if len(sys.argv) > 2:
        try:
            steps = int(sys.argv[2])
        except ValueError:
            logger.info(f"Error: Invalid step count: {sys.argv[2]}")
            return
    
    logger.info(f"Rolling back {steps} migration(s)...")
    
    try:
        from createsonline.database.migrations import migrate_downgrade
        success = migrate_downgrade(steps)
        
        if not success:
            logger.info("Migration rollback failed")
    except Exception as e:
        logger.info(f"Error: {e}")
        import traceback
        traceback.print_exc()

