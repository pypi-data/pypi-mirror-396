"""
CREATESONLINE User Management Commands

Create and manage users for the admin interface.
Lazy imports are used to avoid hard dependencies when not needed.
"""

import logging

_cli_logger = logging.getLogger("createsonline.cli.users")


def createsuperuser_command():
    """Create admin superuser interactively - works with or without rich/typer"""

    # Import dependencies only when command is used
    try:
        import typer
        from rich.console import Console
        from rich.prompt import Prompt, Confirm
        from rich.panel import Panel
        HAS_RICH = True
    except ImportError:
        HAS_RICH = False

    if HAS_RICH:
        # Use rich console for beautiful output
        console = Console()
        console.print(Panel(
            "[bold blue]CREATESONLINE Admin User Creation[/bold blue]\\n\\n"
            "[cyan]Create a superuser account for the admin interface.[/cyan]\\n"
            "[dim]This user will have full administrative privileges.[/dim]",
            title="Create Superuser",
            border_style="blue"
        ))
    else:
        # Fallback to simple print
        console = None
        print("\\n" + "="*60)
        print("CREATESONLINE Admin User Creation")
        print("="*60)
        print("Create a superuser account for the admin interface.")
        print("This user will have full administrative privileges.")
        print("="*60 + "\\n")

    # Get user information
    try:
        if HAS_RICH:
            username = Prompt.ask("[cyan]Username[/cyan]", default="admin")
            email = Prompt.ask("[cyan]Email address[/cyan]", default=f"{username}@example.com")
            password = Prompt.ask("[cyan]Password[/cyan]", password=True)
            password_confirm = Prompt.ask("[cyan]Confirm password[/cyan]", password=True)
        else:
            # Fallback to standard input
            import getpass
            username = input("Username [admin]: ").strip() or "admin"
            email = input(f"Email address [{username}@example.com]: ").strip() or f"{username}@example.com"
            password = getpass.getpass("Password: ")
            password_confirm = getpass.getpass("Confirm password: ")

        if password != password_confirm:
            if HAS_RICH:
                console.print("[red]Passwords don't match![/red]")
                raise typer.Exit(1)
            else:
                print("ERROR: Passwords don't match!")
                return

        # Confirm creation
        if HAS_RICH:
            console.print(f"\\n[green]Creating superuser:[/green]")
            console.print(f"  Username: [cyan]{username}[/cyan]")
            console.print(f"  Email: [cyan]{email}[/cyan]")
            if not Confirm.ask("\\n[yellow]Create this superuser?[/yellow]"):
                console.print("[yellow]Cancelled[/yellow]")
                return
        else:
            print(f"\\nCreating superuser:")
            print(f"  Username: {username}")
            print(f"  Email: {email}")
            confirm = input("\\nCreate this superuser? [Y/n]: ").strip().lower()
            if confirm and confirm not in ['y', 'yes']:
                print("Cancelled")
                return

        # Create the user
        success = create_superuser(username, email, password, console)

        if success:
            if HAS_RICH:
                console.print(Panel(
                    f"[bold green]Success! Superuser '{username}' created successfully![/bold green]\\n\\n"
                    "[cyan]You can now:[/cyan]\\n"
                    "- Login to admin interface\\n"
                    "- Manage users and permissions\\n"
                    "- Configure application settings\\n\\n"
                    "[green]Admin URL:[/green] http://localhost:8000/admin/",
                    title="Success!",
                    border_style="green"
                ))
            else:
                print("\\n" + "="*60)
                print(f"SUCCESS: Superuser '{username}' created successfully!")
                print("="*60)
                print("\\nYou can now:")
                print("  - Login to admin interface")
                print("  - Manage users and permissions")
                print("  - Configure application settings")
                print("\\nAdmin URL: http://localhost:8000/admin/")
                print("="*60 + "\\n")
        else:
            if HAS_RICH:
                console.print("[red]Failed to create superuser[/red]")
                raise typer.Exit(1)
            else:
                print("ERROR: Failed to create superuser")

    except KeyboardInterrupt:
        if HAS_RICH:
            console.print("\\n[yellow]Cancelled by user[/yellow]")
        else:
            print("\\nCancelled by user")
    except Exception as e:
        if HAS_RICH:
            console.print(f"[red]Error creating superuser: {e}[/red]")
            raise typer.Exit(1)
        else:
            print(f"ERROR: Error creating superuser: {e}")
            import traceback
            traceback.print_exc()


def create_superuser(username: str, email: str, password: str, console=None) -> bool:
    """Create a superuser in the database.

    Returns True on success, False otherwise. Accepts optional `console`
    for rich output; falls back to print when not provided.
    """

    try:
        # Try to import models from the current project first
        import sys
        import os
        from urllib.parse import quote_plus
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # Add current directory to path to import project models
        sys.path.insert(0, os.getcwd())
        
        # Get database URL from environment or user_config
        try:
            from user_config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
            # URL-encode password to handle special characters like @, :, /, etc.
            encoded_password = quote_plus(DB_PASSWORD)
            database_url = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        except:
            database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
        
        # Try to import Admin model from project
        try:
            from models import Admin as UserModel
            model_name = "Admin"
        except ImportError:
            # Fallback to framework's User model
            try:
                from createsonline.auth.models import User as UserModel, hash_password as framework_hash
                model_name = "User"
            except ImportError:
                _cli_logger.error("No Admin or User model found. Create an Admin model in models.py")
                return False

        # Create database engine and session
        engine = create_engine(database_url)

        # Create tables if they don't exist
        UserModel.metadata.create_all(engine)

        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()

        try:
            # Check if user already exists
            existing_user = session.query(UserModel).filter(UserModel.username == username).first()
            if existing_user:
                (console.print(f"[yellow]{model_name} '{username}' already exists![/yellow]") if console else _cli_logger.info(f"{model_name} '{username}' already exists!"))
                return False

            # Create the user
            user = UserModel(
                username=username,
                email=email,
                is_active=True,
                is_superuser=True
            )
            
            # Set password using model's method if available, otherwise use hash
            if hasattr(user, 'set_password'):
                user.set_password(password)
            else:
                # Fallback to framework hash
                user.password_hash = framework_hash(password)

            session.add(user)
            session.commit()

            (console.print(f"[green]{model_name} '{username}' created in database[/green]") if console else _cli_logger.info(f"{model_name} '{username}' created in database"))
            return True

        finally:
            session.close()

    except ImportError as e:
        # Fallback to simple file-based storage for demo
        _cli_logger.error(f"Import error: {e}. Configure your database and models.")
        return False
    except Exception as e:
        _cli_logger.error(f"Database error: {e}")
        _cli_logger.info("User creation aborted due to configuration error.")
        return False




