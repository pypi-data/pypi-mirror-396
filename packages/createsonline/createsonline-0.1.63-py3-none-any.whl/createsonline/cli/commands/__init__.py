import logging
_logger = logging.getLogger("createsonline.cli.commands")
# createsonline/cli/commands/__init__.py
"""
CREATESONLINE CLI Commands

Individual command modules for the CREATESONLINE CLI.
FIXED: Lazy imports to prevent dependency crashes when optional packages missing
"""

# Lazy import pattern - don't import commands eagerly
# This prevents ImportError if rich/typer/uvicorn are missing
__all__ = [
    "serve_command",
    "dev_command", 
    "prod_command",
    "info_command",
    "version_command",
    "new_command",
    "shell_command",
    "createsuperuser_command",
    "db_ai_query_command",
    "db_rollback_command", 
    "db_audit_log_command"
]

def _lazy_import_serve():
    """Lazy import serve commands"""
    try:
        from .serve import serve_command, dev_command, prod_command
        return serve_command, dev_command, prod_command
    except ImportError as e:
        def _missing_command(*args, **kwargs):
            _logger.error(f"Command requires additional dependencies: {e}")
            _logger.info("Install with: pip install uvicorn")
            return
        return _missing_command, _missing_command, _missing_command

def _lazy_import_info():
    """Lazy import info commands"""
    try:
        from .info import info_command, version_command
        return info_command, version_command
    except ImportError as e:
        def _missing_command(*args, **kwargs):
            _logger.error(f"Command requires additional dependencies: {e}")
            _logger.info("Install with: pip install rich")
            return
        return _missing_command, _missing_command

def _lazy_import_project():
    """Lazy import project commands"""
    try:
        from .project import new_command
        return new_command
    except ImportError as e:
        def _missing_command(*args, **kwargs):
            _logger.error(f"Command requires additional dependencies: {e}")
            _logger.info("Install with: pip install rich typer")
            return
        return _missing_command

def _lazy_import_shell():
    """Lazy import shell commands"""
    try:
        from .shell import shell_command
        return shell_command
    except ImportError as e:
        def _missing_command(*args, **kwargs):
            _logger.error(f"Command requires additional dependencies: {e}")
            _logger.info("Install with: pip install rich")
            return
        return _missing_command

def _lazy_import_users():
    """Lazy import user commands"""
    try:
        from .users import createsuperuser_command
        return createsuperuser_command
    except ImportError as e:
        def _missing_command(*args, **kwargs):
            _logger.error(f"Command requires additional dependencies: {e}")
            _logger.info("Install with: pip install rich typer")
            return
        return _missing_command

def _lazy_import_database():
    """Lazy import database commands"""
    try:
        from .database import db_ai_query_command, db_rollback_command, db_audit_log_command
        return db_ai_query_command, db_rollback_command, db_audit_log_command
    except ImportError as e:
        def _missing_command(*args, **kwargs):
            _logger.error(f"Database commands require additional dependencies: {e}")
            _logger.info("Install with: pip install rich")
            return
        return _missing_command, _missing_command, _missing_command

# Lazy loading attributes
def __getattr__(name):
    if name == "serve_command":
        return _lazy_import_serve()[0]
    elif name == "dev_command":
        return _lazy_import_serve()[1]
    elif name == "prod_command":
        return _lazy_import_serve()[2]
    elif name == "info_command":
        return _lazy_import_info()[0]
    elif name == "version_command":
        return _lazy_import_info()[1]
    elif name == "new_command":
        return _lazy_import_project()
    elif name == "shell_command":
        return _lazy_import_shell()
    elif name == "createsuperuser_command":
        return _lazy_import_users()
    elif name == "db_ai_query_command":
        return _lazy_import_database()[0]
    elif name == "db_rollback_command":
        return _lazy_import_database()[1]
    elif name == "db_audit_log_command":
        return _lazy_import_database()[2]
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
