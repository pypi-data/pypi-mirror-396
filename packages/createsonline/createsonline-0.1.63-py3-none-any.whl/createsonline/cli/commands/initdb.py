# createsonline/cli/commands/initdb.py
"""
Database initialization command

Creates all tables and initial data.
"""
import os
import sys


def init_database():
    """Initialize database with all tables"""
    print(" Initializing CREATESONLINE database...")
    
    try:
        from sqlalchemy import create_engine
        from createsonline.auth.models import Base as AuthBase, User, Group, Permission, create_default_permissions, create_superuser
        from createsonline.admin.content import Base as ContentBase
        
        # Get database URL
        database_url = os.getenv("DATABASE_URL", "sqlite:///./createsonline.db")
        print(f" Database: {database_url}")
        
        # Create engine
        engine = create_engine(database_url, echo=True)
        
        # Create all tables
        print("\n📦 Creating tables...")
        AuthBase.metadata.create_all(engine)
        ContentBase.metadata.create_all(engine)
        print(" Tables created successfully")
        
        # Create session
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        try:
            # Create default permissions
            print("\n Creating default permissions...")
            permissions = create_default_permissions()
            for perm in permissions:
                # Check if permission already exists
                existing = session.query(Permission).filter_by(
                    codename=perm.codename,
                    content_type=perm.content_type
                ).first()
                
                if not existing:
                    session.add(perm)
                    print(f"   Created permission: {perm.content_type}.{perm.codename}")
            
            session.commit()
            print(" Default permissions created")
            
            # Check if superuser exists
            superuser = session.query(User).filter_by(is_superuser=True).first()
            
            if not superuser:
                print("\n👤 No superuser found. Let's create one!")
                username = input("Username (admin): ").strip() or "admin"
                email = input("Email (admin@createsonline.com): ").strip() or "admin@createsonline.com"
                password = input("Password: ").strip()
                
                if not password:
                    print(" Password cannot be empty")
                    return False
                
                # Create superuser
                superuser = create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                
                session.add(superuser)
                session.commit()
                
                print(f" Superuser '{username}' created successfully!")
                print(f"\n Login credentials:")
                print(f"   Username: {username}")
                print(f"   Password: {password}")
                print(f"\n Start your server and login at /admin")
            else:
                print(f"\n Superuser already exists: {superuser.username}")
            
            # Migrate from superuser.json if exists
            if os.path.exists("superuser.json"):
                print("\n📦 Found superuser.json - migrating...")
                import json
                with open("superuser.json", "r") as f:
                    data = json.load(f)
                    
                    # Check if user already exists
                    existing_user = session.query(User).filter_by(username=data["username"]).first()
                    
                    if not existing_user:
                        migrated_user = User(
                            username=data["username"],
                            email=f"{data['username']}@createsonline.com",
                            password_hash=data["password_hash"],
                            is_staff=True,
                            is_superuser=True,
                            is_active=True,
                            email_verified=True
                        )
                        session.add(migrated_user)
                        session.commit()
                        print(f" Migrated user from superuser.json: {data['username']}")
                    else:
                        print(f"  User {data['username']} already exists - skipping migration")
            
            print("\n Database initialized successfully!")
            print(" You can now run your CREATESONLINE application")
            
            return True
            
        except Exception as e:
            session.rollback()
            print(f"\n Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            session.close()
            
    except ImportError as e:
        print(f"\n Missing dependency: {e}")
        print(" Install SQLAlchemy: pip install sqlalchemy")
        return False
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_superuser_command():
    """Create a new superuser"""
    print("👤 Creating CREATESONLINE superuser...")
    
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from createsonline.auth.models import User, create_superuser
        
        # Get database URL
        database_url = os.getenv("DATABASE_URL", "sqlite:///./createsonline.db")
        print(f" Database: {database_url}")
        
        # Create engine
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        try:
            username = input("Username: ").strip()
            if not username:
                print(" Username cannot be empty")
                return False
            
            # Check if user exists
            existing = session.query(User).filter_by(username=username).first()
            if existing:
                print(f" User '{username}' already exists")
                return False
            
            email = input("Email: ").strip()
            if not email:
                print(" Email cannot be empty")
                return False
            
            password = input("Password: ").strip()
            if not password:
                print(" Password cannot be empty")
                return False
            
            confirm_password = input("Confirm password: ").strip()
            if password != confirm_password:
                print(" Passwords do not match")
                return False
            
            # Create superuser
            user = create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            session.add(user)
            session.commit()
            
            print(f"\n Superuser '{username}' created successfully!")
            print(f" Login at /admin with username: {username}")
            
            return True
            
        except Exception as e:
            session.rollback()
            print(f"\n Error: {e}")
            return False
        finally:
            session.close()
            
    except ImportError as e:
        print(f"\n Missing dependency: {e}")
        print(" Install SQLAlchemy: pip install sqlalchemy")
        return False
    except Exception as e:
        print(f"\n Error: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "createsuperuser":
        create_superuser_command()
    else:
        init_database()
