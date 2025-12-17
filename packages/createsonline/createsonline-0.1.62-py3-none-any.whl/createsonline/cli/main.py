# createsonline/cli/main.py
"""
CREATESONLINE Dynamic CLI - Revolutionary Natural Language Interface

The world's first AI-native framework CLI that understands natural language.
No rigid commands - just express your intent naturally!

Examples:
  createsonline "create new AI-powered project called myapp"
  createsonline "start development server on port 8000"
  createsonline "show comprehensive framework information"
  createsonline "create superuser admin with full access"

Zero external dependencies - pure Python implementation.
"""

import logging
import sys
import os
import re
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Import version for context
from createsonline import __version__

# Python 3.9-3.13 support check
if sys.version_info < (3, 9) or sys.version_info >= (3, 14):
    logging.getLogger("createsonline.cli").error("Unsupported Python version")
    sys.exit(1)

# Optional rich imports with internal fallbacks
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import track
    from rich.prompt import Prompt, Confirm
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

# Optional typer import with internal fallback
try:
    import typer
    TYPER_AVAILABLE = True
except ImportError:
    TYPER_AVAILABLE = False
    # CRITICAL FIX: Create typer stub to prevent crashes
    import types
    typer = types.ModuleType("typer")
    
    # Add stub attributes to prevent AttributeError
    def _typer_stub(*args, **kwargs):
        raise RuntimeError("Typer not installed. Install with: pip install typer")
    
    typer.Typer = _typer_stub
    typer.Argument = _typer_stub
    typer.Option = _typer_stub
    typer.Context = _typer_stub
    typer.Exit = SystemExit


class CreatesonlineInternalConsole:
    """Internal console implementation"""
    
    def __init__(self):
        self.width = 80
        
    def print(self, text: str, style: str = ""):
        """Print with optional styling"""
        # Simple color codes for terminals that support them
        colors = {
            "red": "\033[91m",
            "green": "\033[92m", 
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "cyan": "\033[96m",
            "white": "\033[97m",
            "bold": "\033[1m",
            "reset": "\033[0m"
        }
        
        if "red" in style:
            print(f"{colors.get('red', '')}{text}{colors.get('reset', '')}")
        elif "green" in style:
            print(f"{colors.get('green', '')}{text}{colors.get('reset', '')}")
        elif "yellow" in style:
            print(f"{colors.get('yellow', '')}{text}{colors.get('reset', '')}")
        elif "blue" in style:
            print(f"{colors.get('blue', '')}{text}{colors.get('reset', '')}")
        elif "cyan" in style:
            print(f"{colors.get('cyan', '')}{text}{colors.get('reset', '')}")
        elif "bold" in style:
            print(f"{colors.get('bold', '')}{text}{colors.get('reset', '')}")
        else:
            print(text)
    
    def panel(self, text: str, title: str = "", border_style: str = ""):
        """Create a simple panel"""
        lines = text.split('\n')
        max_width = max(len(line) for line in lines) if lines else 0
        panel_width = max(max_width + 4, len(title) + 4, 40)
        
        # Top border
        if title:
            title_line = f"â”Œâ”€ {title} " + "â”€" * (panel_width - len(title) - 4) + "â”"
        else:
            title_line = "â”Œ" + "â”€" * (panel_width - 2) + "â”"
        
        print(title_line)
        
        # Content
        for line in lines:
            padded_line = f"â”‚ {line:<{panel_width-4}} â”‚"
            print(padded_line)
        
        # Bottom border
        print("â””" + "â”€" * (panel_width - 2) + "â”˜")
    
    def table(self, data: List[List[str]], headers: List[str] = None):
        """Create a simple table"""
        if not data:
            return
        
        # Calculate column widths
        if headers:
            all_rows = [headers] + data
        else:
            all_rows = data
        
        col_widths = []
        for col_idx in range(len(all_rows[0])):
            max_width = max(len(str(row[col_idx])) for row in all_rows if col_idx < len(row))
            col_widths.append(max_width + 2)
        
        # Print headers
        if headers:
            header_line = "|".join(f" {headers[i]:<{col_widths[i]-1}}" for i in range(len(headers)))
            print(header_line)
            print("-" * len(header_line))
        
        # Print data
        for row in data:
            row_line = "|".join(f" {str(row[i]):<{col_widths[i]-1}}" if i < len(row) else f" {'':<{col_widths[i]-1}}" for i in range(len(col_widths)))
            print(row_line)


class CreatesonlineNaturalLanguageCLI:
    """
    Revolutionary Natural Language CLI for CREATESONLINE
    
    Understands user intent through natural language processing
    without external NLP dependencies - pure Python pattern matching.
    """
    
    def __init__(self):
        self.console = console if RICH_AVAILABLE else CreatesonlineInternalConsole()
        self.commands_db = self._build_commands_database()
        self.context = {
            "last_command": None,
            "current_directory": os.getcwd(),
            "framework_version": __version__
        }
    
    def _build_commands_database(self) -> Dict[str, Dict[str, Any]]:
        """Build natural language commands database"""
        return {
            # Project Management
            "create_project": {
                "patterns": [
                    r"create\s+(new\s+)?project\s+(called\s+|named\s+)?(\w+)",
                    r"new\s+project\s+(\w+)",
                    r"make\s+(a\s+)?project\s+(\w+)",
                    r"generate\s+project\s+(\w+)",
                    r"init\s+project\s+(\w+)"
                ],
                "handler": "handle_create_project",
                "description": "Create a new CREATESONLINE project",
                "examples": [
                    'create new project called myapp',
                    'new project blog',
                    'make a project ecommerce'
                ]
            },
            
            # Project Initialization
            "init_project": {
                "patterns": [
                    r"^init(ialize)?\s*$",
                    r"^init(ialize)?\s+project\s*$",
                    r"^setup\s+project\s*$",
                    r"^bootstrap\s+project\s*$"
                ],
                "handler": "handle_init_project",
                "description": "Initialize project structure in current directory",
                "examples": [
                    'init',
                    'initialize project',
                    'setup project'
                ]
            },
            
            # Server Management
            "start_server": {
                "patterns": [
                    # FIXED: Added word boundaries and more specific patterns
                    r"^start\s+(development|dev)\s+server(\s+on\s+port\s+(\d+))?\b",
                    r"^run\s+(dev|development)\s+server(\s+port\s+(\d+))?\b",
                    r"^serve\s+dev(elopment)?(\s+on\s+(\d+))?\b",
                    r"^dev\s+server(\s+port\s+(\d+))?\b"
                ],
                "handler": "handle_start_server",
                "description": "Start development server",
                "examples": [
                    'start development server',
                    'start server on port 8000',
                    'run dev server with hot reload',
                    'serve development on port 8080'
                ]
            },
            
            # Production Server
            "production_server": {
                "patterns": [
                    # FIXED: More specific production patterns
                    r"^start\s+production\s+server(\s+with\s+(\d+)\s+workers)?\b",
                    r"^run\s+prod(uction)?\s+server(\s+(\d+)\s+workers)?\b",
                    r"^production\s+mode(\s+(\d+)\s+workers)?\b",
                    r"^serve\s+production(\s+(\d+)\s+workers)?\b"
                ],
                "handler": "handle_production_server",
                "description": "Start production server",
                "examples": [
                    'start production server',
                    'run prod server with 4 workers',
                    'production mode'
                ]
            },
            
            # Information Commands
            "framework_info": {
                "patterns": [
                    # FIXED: More specific info patterns to avoid conflicts
                    r"^show\s+(me\s+)?(framework\s+)?info(rmation)?\b",
                    r"^what\s+is\s+createsonline\b",
                    r"^framework\s+details\b",
                    r"^info\s*$",  # Exact match for just "info"
                    r"^about\s+(createsonline|framework)\b"
                ],
                "handler": "handle_framework_info",
                "description": "Show framework information",
                "examples": [
                    'show me framework info',
                    'what is createsonline',
                    'info'
                ]
            },
            
            # Version Information  
            "version": {
                "patterns": [
                    # FIXED: Exact version patterns to avoid matching "conversion" etc
                    r"^version\s*$",
                    r"^show\s+version\b",
                    r"^what\s+version\b",
                    r"^\-\-version\s*$",
                    r"^v\s*$"  # Just "v" alone
                ],
                "handler": "handle_version",
                "description": "Show version information",
                "examples": [
                    'version',
                    'what version',
                    'show version'
                ]
            },
            
            # User Management
            "create_superuser": {
                "patterns": [
                    r"create\s+(super)?user(\s+(called\s+|named\s+)?(\w+))?",
                    r"add\s+(super)?user(\s+(\w+))?",
                    r"make\s+(super)?user(\s+(\w+))?",
                    r"new\s+(super)?user(\s+(\w+))?"
                ],
                "handler": "handle_create_superuser",
                "description": "Create admin superuser",
                "examples": [
                    'create superuser',
                    'add user admin',
                    'create superuser called john'
                ]
            },
            
            # Shell Access
            "shell": {
                "patterns": [
                    r"shell",
                    r"interactive\s+shell",
                    r"python\s+shell",
                    r"repl"
                ],
                "handler": "handle_shell",
                "description": "Start interactive shell",
                "examples": [
                    'shell',
                    'interactive shell',
                    'python shell'
                ]
            },
            
            # Help System
            "help": {
                "patterns": [
                    r"help",
                    r"what\s+can\s+(i|you)\s+do",
                    r"commands",
                    r"usage",
                    r"\?"
                ],
                "handler": "handle_help",
                "description": "Show available commands",
                "examples": [
                    'help',
                    'what can you do',
                    'commands'
                ]
            },
            
            # AI Features
            "ai_Example": {
                "patterns": [
                    r"show\s+ai\s+(Example|features|capabilities)",
                    r"ai\s+Example",
                    r"Examplenstrate\s+ai",
                    r"what\s+ai\s+features"
                ],
                "handler": "handle_ai_Example",
                "description": "Examplenstrate AI capabilities",
                "examples": [
                    'show ai Example',
                    'ai features',
                    'Examplenstrate ai'
                ]
            },
            
            # Database AI Query
            "db_ai_query": {
                "patterns": [
                    r"db\s+ai-query\s+(.+)",
                    r"database\s+query\s+(.+)",
                    r"ai\s+query\s+(.+)",
                    r"query\s+database\s+(.+)"
                ],
                "handler": "handle_db_ai_query",
                "description": "Query database using natural language",
                "examples": [
                    'db ai-query "show last 10 users"',
                    'database query "count all sessions"',
                    'ai query "show errors"'
                ]
            },
            
            # Database Rollback
            "db_rollback": {
                "patterns": [
                    r"db\s+rollback(\s+(\d+))?",
                    r"database\s+rollback(\s+(\d+))?",
                    r"rollback\s+database(\s+(\d+))?"
                ],
                "handler": "handle_db_rollback",
                "description": "Rollback database operations",
                "examples": [
                    'db rollback',
                    'database rollback 5',
                    'rollback last 3 operations'
                ]
            },
            
            # Database Audit Log
            "db_audit_log": {
                "patterns": [
                    r"db\s+audit-log(\s+(\d+))?",
                    r"database\s+audit(\s+(\d+))?",
                    r"show\s+audit\s+log(\s+(\d+))?",
                    r"audit\s+trail(\s+(\d+))?"
                ],
                "handler": "handle_db_audit_log",
                "description": "Show database audit log",
                "examples": [
                    'db audit-log',
                    'database audit 10',
                    'show audit log'
                ]
            }
        }
    
    def parse_natural_language(self, input_text: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Parse natural language input and extract intent + parameters
        
        Returns:
            (command_name, parameters_dict)
        """
        input_text = input_text.lower().strip()
        
        for command_name, command_data in self.commands_db.items():
            for pattern in command_data["patterns"]:
                match = re.search(pattern, input_text)
                if match:
                    # Extract parameters from regex groups
                    params = self._extract_parameters(command_name, match, input_text)
                    return command_name, params
        
        return None, {}
    
    def _extract_parameters(self, command_name: str, match: re.Match, full_text: str) -> Dict[str, Any]:
        """Extract parameters from regex match - FIXED: Improved stop-word filtering"""
        params = {}
        groups = match.groups()
        
        # FIXED: Better stop words list with more specific filtering
        STOP_WORDS = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'new', 'called', 'named', 'create', 'start', 'make', 'run', 'launch', 'serve',
            'super', 'admin', 'user', 'project', 'server', 'app', 'application'
        }
        
        if command_name == "create_project":
            # Extract project name - FIXED: Better filtering
            for group in groups:
                if group and group.strip():
                    clean_name = group.strip().lower()
                    # FIXED: More strict validation - avoid common words
                    if (clean_name not in STOP_WORDS and 
                        len(clean_name) > 2 and  # Must be longer than 2 chars
                        not clean_name.isdigit() and  # Not just numbers
                        clean_name.replace('_', '').replace('-', '').isalnum()):  # Valid identifier chars
                        params['project_name'] = group.strip()
                        break
            
            # Default fallback if no valid name found
            if 'project_name' not in params:
                params['project_name'] = 'my_project'
            
            # Check for AI features
            if 'ai' in full_text or 'artificial intelligence' in full_text:
                params['ai_features'] = True
            if 'admin' in full_text:
                params['admin_enabled'] = True
            if 'auth' in full_text or 'authentication' in full_text:
                params['auth_enabled'] = True
        
        elif command_name in ["start_server", "production_server"]:
            # Extract port number
            for group in groups:
                if group and group.isdigit():
                    port_num = int(group)
                    # FIXED: Validate reasonable port range
                    if 1000 <= port_num <= 65535:
                        params['port'] = port_num
                        break
            
            # FIXED: Better worker extraction for production
            if command_name == "production_server":
                # Look for explicit worker mentions, not just any number
                for group in groups:
                    if group and group.isdigit():
                        worker_count = int(group)
                        if 1 <= worker_count <= 16:  # Reasonable worker range
                            params['workers'] = worker_count
                            break
                
        elif command_name == "db_ai_query":
            # Extract the natural language query
            for group in groups:
                if group and group.strip():
                    # Clean up quotes and whitespace
                    query = group.strip().strip('"\'')
                    if query:
                        params['query'] = query
                        break
        
        elif command_name == "db_rollback":
            # Extract count for rollback
            for group in groups:
                if group and group.isdigit():
                    count = int(group)
                    if 1 <= count <= 100:  # Reasonable limit
                        params['count'] = count
                        break
            if 'count' not in params:
                params['count'] = 1  # Default rollback count
        
        elif command_name == "db_audit_log":
            # Extract limit for audit log
            for group in groups:
                if group and group.isdigit():
                    limit = int(group)
                    if 1 <= limit <= 1000:  # Reasonable limit
                        params['limit'] = limit
                        break
            if 'limit' not in params:
                params['limit'] = 10  # Default limit
                if re.search(r'(\d+)\s*workers?', full_text, re.IGNORECASE):
                    worker_match = re.search(r'(\d+)\s*workers?', full_text, re.IGNORECASE)
                    if worker_match:
                        params['workers'] = int(worker_match.group(1))
                else:
                    params['workers'] = 4  # Reasonable default for production
        
        elif command_name == "create_superuser":
            # Extract username - FIXED: Better validation
            for group in groups:
                if group and group.strip():
                    clean_username = group.strip().lower()
                    if (clean_username not in STOP_WORDS and 
                        len(clean_username) >= 3 and
                        clean_username.replace('_', '').isalnum()):
                        params['username'] = group.strip()
                        break
            
            # Default fallback
            if 'username' not in params:
                params['username'] = 'admin'
        
        return params
    
    async def execute_command(self, command_name: str, params: Dict[str, Any]) -> bool:
        """Execute the parsed command"""
        
        if command_name not in self.commands_db:
            return False
        
        handler_name = self.commands_db[command_name]["handler"]
        handler = getattr(self, handler_name, None)
        
        if handler:
            try:
                await handler(params)
                self.context["last_command"] = command_name
                return True
            except Exception as e:
                self._error(f"Command execution failed: {e}")
                return False
        
        return False
    
    # ========================================
    # COMMAND HANDLERS
    # ========================================
    
    async def handle_create_project(self, params: Dict[str, Any]):
        """Handle project creation with natural language parameters"""
        project_name = params.get('project_name', 'my_createsonline_app')
        ai_features = params.get('ai_features', True)  # Default to True for AI-native framework
        admin_enabled = params.get('admin_enabled', True)
        auth_enabled = params.get('auth_enabled', True)
        
        self._info(f"Creating CREATESONLINE project: {project_name}")
        
        # Show project configuration
        config_data = [
            ["Feature", "Status"],
            ["AI Features", "Enabled" if ai_features else "Disabled"],
            ["Admin Interface", "Enabled" if admin_enabled else "Disabled"],
            ["Authentication", "Enabled" if auth_enabled else "Disabled"]
        ]
        
        if RICH_AVAILABLE:
            table = Table(title="Project Configuration")
            table.add_column("Feature", style="cyan")
            table.add_column("Status", style="green")
            for row in config_data[1:]:
                table.add_row(row[0], row[1])
            console.print(table)
        else:
            self.console.table(config_data[1:], config_data[0])
        
        # Create project structure
        await self._create_project_structure(project_name, ai_features, admin_enabled, auth_enabled)
        
        # Show next steps
        self._success(f"Project '{project_name}' created successfully!")
        self._info("Next steps:")
        self._info(f"1. cd {project_name}")
        self._info("2. python -m venv venv")
        self._info("3. source venv/bin/activate  # Windows: venv\\Scripts\\activate")
        self._info("4. pip install -r requirements.txt")
        self._info("5. createsonline 'start development server'")
    
    async def handle_init_project(self, params: Dict[str, Any]):
        """Initialize project structure in current directory"""
        try:
            from createsonline.project_init import ProjectInitializer
            
            self._info("Initializing CREATESONLINE project structure...")
            
            # Get current directory
            project_root = Path.cwd()
            self._info(f"Project root: {project_root}")
            
            # Initialize project with verbose output for CLI
            initializer = ProjectInitializer(project_root)
            result = initializer.initialize(verbose=True)
            
            # Show results
            if result.get("success"):
                created_files = result.get("created_files", [])
                skipped_files = result.get("user_files_skipped", [])
                created_dirs = result.get("created_directories", [])
                
                # Show created directories
                for dir_path in created_dirs:
                    self._info(f"   Created directory: {dir_path}")
                
                # Show created files
                for file_info in created_files:
                    self._info(f"   Created {file_info['type']}: {file_info['path']}")
                
                # Show skipped files (user customizations)
                if skipped_files:
                    self._warning(f"\nSkipped {len(skipped_files)} existing file(s) to preserve your customizations:")
                    for filepath in skipped_files:
                        self._info(f"   * {filepath}")
                
                self._success(f"\nInitialization complete!")
                self._info(f"Created {len(created_files)} new files")
                
                if skipped_files:
                    self._info(f"Protected {len(skipped_files)} existing files")
                
                # Show next steps
                self._info("\nNext steps:")
                self._info("   1. Edit routes.py to add your custom routes")
                self._info("   2. Customize templates/ and static/ folders")
                self._info("   3. Run: python main.py")
                self._success("\nHappy coding!")
                
            else:
                self._error("Initialization failed")
                error_msg = result.get("error", "Unknown error")
                self._error(f"Error: {error_msg}")
                
        except ImportError:
            self._error("ProjectInitializer not found. Please upgrade createsonline:")
            self._info("   pip install --upgrade createsonline")
        except Exception as e:
            self._error(f"Initialization failed: {e}")
            import traceback
            self._error(traceback.format_exc())
    
    async def handle_start_server(self, params: Dict[str, Any]):
        """Handle development server startup"""
        port = params.get('port', 8000)
        host = params.get('host', '0.0.0.0')
        reload = params.get('reload', True)  # Auto-reload enabled by default in dev
        
        # Check for application files
        app_files = ["main.py", "app.py"]
        app_file = None
        
        for file in app_files:
            if Path(file).exists():
                app_file = file
                break
        
        if not app_file:
            await self._create_basic_app()
            app_file = "main.py"
        
        try:
            # Pass port, host, and reload as environment variables
            env = os.environ.copy()
            env['PORT'] = str(port)
            env['HOST'] = host
            env['RELOAD'] = '1' if reload else '0'
            
            # Use internal pure Python server - no uvicorn needed!
            subprocess.run([
                sys.executable, app_file
            ], env=env)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self._error(f"Error: {e}")
    
    async def handle_production_server(self, params: Dict[str, Any]):
        """Handle production server startup"""
        port = params.get('port', 8000)
        workers = params.get('workers', 4)
        
        self._info(f"Starting CREATESONLINE production server with {workers} workers")
        
        # Production configuration
        self._panel_info("Production Server", f"""
ðŸ­ CREATESONLINE Production Mode
âš¡ Workers: {workers}
ðŸŒ Port: {port}
ðŸ”’ Security: Enabled
ðŸ“Š Monitoring: Active
        """)
        
        try:
            # Use internal pure Python server - production mode
            # Note: For true multi-worker support, consider using gunicorn with the internal server
            subprocess.run([
                sys.executable, "main.py"
            ])
        except Exception as e:
            self._error(f"Production server failed: {e}")
    
    async def handle_framework_info(self, params: Dict[str, Any]):
        """Show comprehensive framework information"""
        
        # Framework banner
        banner = """
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘                        CREATESONLINE                         â•‘
â•‘                  The AI-Native Web Framework                 â•‘
â•‘                                                              â•‘
â•‘                 Build Intelligence Into Everything           â•‘
â•‘                                                              â•‘
â•‘  Version: 0.1.0    | Python: 3.9-3.13                        â•‘
â•‘  Pure Framework | AI-First | Pure Python                  â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        """.strip()
        
        self._info(banner)
        
        # Features table
        features_data = [
            ["Feature", "Status", "Description"],
            ["AI-Native Core", "Active", "Built-in AI capabilities"],
            ["Pure Python", "Active", "Works with just Python"],
            ["Dynamic CLI", "Active", "Natural language commands"],
            ["Admin Interface", "Ready", "Built-in admin panel"],
            ["User Management", "Ready", "Built-in authentication"],
            ["Vector Search", "Ready", "Semantic similarity"],
            ["LLM Integration", "ðŸ”„ Optional", "When API keys provided"],
            ["Auto Templates", "Active", "Internal template system"]
        ]
        
        if RICH_AVAILABLE:
            table = Table(title="Framework Features")
            table.add_column("Feature", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Description", style="white")
            for row in features_data[1:]:
                table.add_row(row[0], row[1], row[2])
            console.print(table)
        else:
            self.console.table(features_data[1:], features_data[0])
        
        # Natural language examples
        self._panel_info("Natural Language CLI Examples", """
â€¢ "create new AI-powered project called blog"
â€¢ "start development server on port 8000"
â€¢ "launch production server with 4 workers"
â€¢ "create superuser admin with full permissions"
â€¢ "show available AI capabilities and features"
â€¢ "start server in development mode"
â€¢ "display framework information and status"
        """)
    
    async def handle_version(self, params: Dict[str, Any]):
        """Show version information"""
        
        # Reference to our logo files
        logo_path = os.path.join(os.path.dirname(__file__), "..", "static", "image")
        favicon_files = ["favicon.svg", "favicon.ico", "logo.png"]
        
        version_info = f"""
ï¼£âŽ¯â— CREATESONLINE Framework v0.1.0 - Ultimate Pure Independence

ðŸ Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}
ðŸ–¥ï¸  Platform: {sys.platform}
ðŸ“ Location: {os.path.dirname(__file__)}
ðŸŽ¯ Mode: {'Enhanced' if RICH_AVAILABLE else 'Core'}
ðŸŽ¨ Brand Assets: {logo_path}

Build Intelligence Into Everything
        """.strip()
        
        self._panel_info("Version Information", version_info)
    
    async def handle_create_superuser(self, params: Dict[str, Any]):
        """Handle superuser creation - call the real implementation"""
        try:
            from createsonline.cli.commands import createsuperuser_command
            createsuperuser_command()
        except Exception as e:
            self._error(f"Error creating superuser: {e}")
    
    async def handle_shell(self, params: Dict[str, Any]):
        """Start interactive shell"""
        self._info("Starting CREATESONLINE interactive shell...")
        
        try:
            # Try to start Python shell with CREATESONLINE imports
            code = '''
import sys
sys.path.insert(0, ".")

# Try to import CREATESONLINE
try:
    import createsonline
    print("[OK] CREATESONLINE imported successfully")
    print("Available: createsonline.create_app()")
except ImportError:
    print("âš ï¸  CREATESONLINE not in Python path")

print("ðŸš CREATESONLINE Interactive Shell")
logging.getLogger("createsonline.cli").info("Type exit() to quit")
            '''
            
            # Start Python with the code
            subprocess.run([sys.executable, "-i", "-c", code])
            
        except KeyboardInterrupt:
            self._info("Shell session ended")
    
    async def handle_help(self, params: Dict[str, Any]):
        """Show help information"""
        
        self._panel_info("ï¼£âŽ¯â— CREATESONLINE Natural Language CLI", """
ðŸŽ¯ Express your intent naturally - no rigid commands needed!

Examples of what you can say:
        """)
        
        # Group commands by category
        categories = {
            "Project Management": ["create_project"],
            "Server Operations": ["start_server", "production_server"], 
            "User Management": ["create_superuser"],
            "Information": ["framework_info", "version", "help"],
            "Development": ["shell", "ai_Example"]
        }
        
        for category, command_names in categories.items():
            self._info(f"\nðŸ“‚ {category}:")
            for cmd_name in command_names:
                if cmd_name in self.commands_db:
                    examples = self.commands_db[cmd_name]["examples"]
                    for example in examples[:2]:  # Show first 2 examples
                        self._info(f"   â€¢ createsonline \"{example}\"")
    
    async def handle_ai_Example(self, params: Dict[str, Any]):
        """Examplenstrate AI capabilities"""
        
        self._panel_info("CREATESONLINE AI Capabilities", """
ðŸ§  Built-in AI Features:

â€¢ Hash-based Embeddings - Consistent vector representations
â€¢ Rule-based Generation - Smart text creation
â€¢ Similarity Search - Find related content
â€¢ AI Field Types - Database fields with intelligence
â€¢ Mock AI Services - Development-ready AI

ðŸ”¥ Enhanced AI (With API Keys):

â€¢ OpenAI Integration - GPT models for generation
â€¢ Anthropic Claude - Advanced reasoning
â€¢ Vector Databases - Production embeddings
â€¢ Real-time Learning - Adaptive algorithms
        """)
        
        # Show AI field examples
        self._info("\nðŸŽ¯ AI Field Examples:")
        self._info("   â€¢ AIComputedField - Automatic ML predictions")
        self._info("   â€¢ LLMField - Content generation")  
        self._info("   â€¢ VectorField - Semantic search")
        self._info("   â€¢ SmartTextField - Text analysis")

    async def handle_db_ai_query(self, params: Dict[str, Any]):
        """Handle database AI query command"""
        query = params.get('query', '')
        if not query:
            self._error("No query provided. Usage: db ai-query 'show last 10 users'")
            return
            
        try:
            # Import the database AI query command
            from createsonline.cli.commands.database import db_ai_query_command
            db_ai_query_command(query)  # Remove await - function is not async
        except ImportError as e:
            self._error(f"Database commands not available: {e}")
        except Exception as e:
            self._error(f"Query failed: {e}")

    async def handle_db_rollback(self, params: Dict[str, Any]):
        """Handle database rollback command"""
        count = params.get('count', 1)
        
        try:
            # Import the database rollback command
            from createsonline.cli.commands.database import db_rollback_command
            db_rollback_command(count)  # Remove await - function is not async
        except ImportError as e:
            self._error(f"Database commands not available: {e}")
        except Exception as e:
            self._error(f"Rollback failed: {e}")

    async def handle_db_audit_log(self, params: Dict[str, Any]):
        """Handle database audit log command"""
        limit = params.get('limit', 10)
        
        try:
            # Import the database audit log command
            from createsonline.cli.commands.database import db_audit_log_command
            db_audit_log_command(limit)  # Remove await - function is not async
        except ImportError as e:
            self._error(f"Database commands not available: {e}")
        except Exception as e:
            self._error(f"Audit log failed: {e}")
        
        try:
            # Import the database audit log command
            from createsonline.cli.commands.database import db_audit_log_command
            await db_audit_log_command(limit)
        except ImportError as e:
            self._error(f"Database commands not available: {e}")
        except Exception as e:
            self._error(f"Audit log failed: {e}")
    
    # ========================================
    # UTILITY METHODS
    # ========================================
    
    def _info(self, message: str):
        """Print info message"""
        if RICH_AVAILABLE:
            console.print(message, style="blue")
        else:
            self.console.print(message, "blue")
    
    def _success(self, message: str):
        """Print success message"""
        if RICH_AVAILABLE:
            console.print(f"[SUCCESS] {message}", style="green")
        else:
            self.console.print(f"[SUCCESS] {message}", "green")
    
    def _warning(self, message: str):
        """Print warning message"""
        if RICH_AVAILABLE:
            console.print(f"âš ï¸ {message}", style="yellow")
        else:
            self.console.print(f"âš ï¸ {message}", "yellow")
    
    def _error(self, message: str):
        """Print error message"""
        if RICH_AVAILABLE:
            console.print(f"[ERROR] {message}", style="red")
        else:
            self.console.print(f"[ERROR] {message}", "red")
    
    def _panel_info(self, title: str, content: str):
        """Print panel with info"""
        if RICH_AVAILABLE:
            console.print(Panel(content.strip(), title=title, border_style="blue"))
        else:
            self.console.panel(content.strip(), title)
    
    async def _create_project_structure(self, project_name: str, ai_features: bool, admin_enabled: bool, auth_enabled: bool):
        """Create project directory structure"""
        
        project_path = Path(project_name)
        if project_path.exists():
            self._warning(f"Directory '{project_name}' already exists")
            return
        
        # Create directories
        project_path.mkdir()
        (project_path / "static").mkdir()
        (project_path / "templates").mkdir()
        
        # Generate main.py
        main_content = self._generate_main_py(project_name, ai_features, admin_enabled, auth_enabled)
        (project_path / "main.py").write_text(main_content)
        
        # Generate requirements.txt - Pure CREATESONLINE, no external server needed!
        requirements = "createsonline"
        if ai_features:
            requirements += "\n\n# AI Features (optional)\n# openai>=1.0.0\n# numpy>=1.24.0"
        (project_path / "requirements.txt").write_text(requirements)
        
        # Generate .env
        env_content = f"""# {project_name} Configuration
DEBUG=true
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///./app.db
HOST=0.0.0.0
PORT=8000

# AI Configuration (optional)
# OPENAI_API_KEY=your-key-here
"""
        (project_path / ".env").write_text(env_content)
        
        # Generate routes.py with actual routes
        routes_content = f'''"""
{project_name} Routes

All application routes are defined here.
"""
from main import app


@app.get("/")
async def home(request):
    """Home page"""
    return {{
        "message": "Welcome to {project_name.title()}!",
        "framework": "CREATESONLINE",
        "ai_enabled": {str(ai_features).lower()},
        "admin_enabled": {str(admin_enabled).lower()},
        "auth_enabled": {str(auth_enabled).lower()},
        "status": "operational"
    }}


@app.get("/api/status")
async def api_status(request):
    """API status"""
    return {{
        "service": "{project_name.title()} API",
        "status": "operational",
        "framework": "CREATESONLINE",
        "version": "1.0.0"
    }}


@app.get("/health")
async def health(request):
    """Health check"""
    return {{"status": "healthy", "framework": "CREATESONLINE"}}


# Add your custom routes below
# Example:
# @app.post("/api/users")
# async def create_user(request):
#     data = await request.json()
#     return {{"message": "User created", "data": data}}
'''
        (project_path / "routes.py").write_text(routes_content)
        
        # Generate .gitignore
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log

# OS
.DS_Store
Thumbs.db
"""
        (project_path / ".gitignore").write_text(gitignore_content)
        
        # Create basic HTML template
        template_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name.title()} - CREATESONLINE</title>
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }}
        .container {{
            text-align: center;
            padding: 2rem;
        }}
        h1 {{
            font-size: 3rem;
            margin-bottom: 1rem;
            animation: fadeIn 1s ease-in;
        }}
        p {{
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 2rem;
        }}
        .badge {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            margin: 0.5rem;
            backdrop-filter: blur(10px);
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{project_name.title()}</h1>
        <p>Built with CREATESONLINE - The AI-Native Web Framework</p>
        <div>
            <span class="badge">CREATESONLINE v1.42.0</span>
            <span class="badge">Python</span>
            <span class="badge">AI-Powered</span>
        </div>
    </div>
</body>
</html>
"""
        (project_path / "templates" / "index.html").write_text(template_content)
        
        # Create basic CSS file
        css_content = """/* {project_name} Styles */

:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --text-color: #333;
    --bg-color: #f5f5f5;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    color: var(--text-color);
    background-color: var(--bg-color);
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

/* Add your custom styles below */
"""
        (project_path / "static" / "css").mkdir(parents=True, exist_ok=True)
        (project_path / "static" / "css" / "style.css").write_text(css_content)
        
        # Create placeholder for favicon (SVG format)
        favicon_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
  </defs>
  <circle cx="50" cy="50" r="45" fill="url(#grad)" />
  <text x="50" y="65" font-size="50" font-weight="bold" fill="white" text-anchor="middle" font-family="Arial">C</text>
</svg>'''
        (project_path / "static" / "favicon.svg").write_text(favicon_svg)
        
        # Generate README.md
        readme_content = f"""# {project_name}

Built with **CREATESONLINE** - The AI-Native Web Framework

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start development server
createsonline "start development server"

# Or traditionally
python main.py
```

## Natural Language CLI

```bash
createsonline "show comprehensive framework information"
createsonline "create superuser admin with full permissions"
createsonline "start development server on port 8000"
```

Built with Intelligence Into Everything
"""
        (project_path / "README.md").write_text(readme_content)
    
    def _generate_main_py(self, project_name: str, ai_features: bool, admin_enabled: bool, auth_enabled: bool) -> str:
        """Generate main.py content"""
        
        ai_config = {}
        if ai_features:
            ai_config = {
                "enable_smart_fields": True,
                "default_llm": "internal"
            }
        
        return f'''#!/usr/bin/env python3
"""
{project_name} - CREATESONLINE Application

Built with CREATESONLINE - The AI-Native Web Framework
Created with natural language: "create project {project_name}"
"""
from createsonline import create_app

# Create CREATESONLINE application
app = create_app(
    title="{project_name.title()}",
    description="AI-powered application built with CREATESONLINE",
    version="1.0.0",
    ai_config={ai_config},
    debug=False
)

{f"# Enable AI features\\napp.enable_ai_features(['smart_query', 'content_generation', 'vector_search'])" if ai_features else ""}

# Import routes from routes.py
import routes

if __name__ == "__main__":
    import os
    from createsonline.server import run_server
    
    # Load environment variables from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "1") == "1"  # Auto-reload in development
    
    run_server(app, host=host, port=port, reload=reload)
'''
    
    async def _create_basic_app(self):
        """Create basic application file if none exists or update if outdated"""
        
        TEMPLATE_VERSION = "0.1.1"
        
        # Check if main.py exists and has version marker
        if Path("main.py").exists():
            content = Path("main.py").read_text(encoding='utf-8')
            # Check if it's our auto-generated template
            if "Auto-generated by CREATESONLINE CLI" in content:
                # Extract version from existing file
                import re
                version_match = re.search(r'Template Version: ([\d.]+)', content)
                if version_match:
                    existing_version = version_match.group(1)
                    if existing_version == TEMPLATE_VERSION:
                        # Already up to date, don't regenerate
                        return
                    else:
                        self._info(f"Updating main.py from v{existing_version} to v{TEMPLATE_VERSION}")
                else:
                    # Old template without version, update it
                    self._info("Updating main.py to latest template")
            else:
                # User's custom main.py, don't touch it
                return
        
        # Build template with version header
        version_header = f'''#!/usr/bin/env python3
"""
Basic CREATESONLINE Application

Auto-generated by CREATESONLINE CLI
Template Version: {TEMPLATE_VERSION}
"""
'''
        
        basic_app = version_header + '''from createsonline import create_app

# Create basic CREATESONLINE application
app = create_app(
    title="CREATESONLINE Example",
    description="Basic CREATESONLINE application",
    version="1.0.0",
    debug=False
)

@app.get("/")
async def home(request):
    """Home page with beautiful UI"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CREATESONLINE Framework</title>
        
        <!-- Favicons -->
        <link rel="icon" type="image/x-icon" href="/favicon.ico">
        <link rel="icon" type="image/png" sizes="32x32" href="/icons/icon-32x32.png">
        <link rel="icon" type="image/png" sizes="16x16" href="/icons/icon-16x16.png">
        <link rel="apple-touch-icon" sizes="180x180" href="/icons/icon-180x180.png">
        <link rel="manifest" href="/site.webmanifest">
        
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #000000 0%, #1a1a1a 50%, #000000 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
                position: relative;
                overflow: hidden;
            }}
            
            body::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: repeating-linear-gradient(
                    0deg,
                    transparent,
                    transparent 2px,
                    rgba(255, 255, 255, 0.03) 2px,
                    rgba(255, 255, 255, 0.03) 4px
                );
                animation: scan 8s linear infinite;
                pointer-events: none;
            }}
            
            @keyframes scan {{
                0% {{ transform: translateY(0); }}
                100% {{ transform: translateY(50px); }}
            }}
            
            .container {{
                background: rgba(255, 255, 255, 0.98);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(0, 0, 0, 0.1);
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                padding: 80px 60px;
                max-width: 1000px;
                width: 100%;
                animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
                position: relative;
                z-index: 1;
            }}
            
            @keyframes slideUp {{
                from {{
                    opacity: 0;
                    transform: translateY(30px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .logo {{
                display: block;
                margin: 0 auto 50px;
                max-width: 280px;
                width: 100%;
                height: auto;
                filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
            }}
            
            h1 {{
                font-size: 2.8em;
                color: #000000;
                margin-bottom: 15px;
                text-align: center;
                font-weight: 300;
                letter-spacing: -1px;
                position: relative;
            }}
            
            h1::after {{
                content: '';
                display: block;
                width: 60px;
                height: 3px;
                background: #000000;
                margin: 20px auto 0;
            }}
            
            .subtitle {{
                text-align: center;
                color: #666666;
                font-size: 1.1em;
                margin-bottom: 50px;
                font-weight: 300;
                line-height: 1.6;
            }}
            
            .links {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 25px;
                margin: 50px 0;
            }}
            
            .link-card {{
                background: #000000;
                padding: 40px 30px;
                text-decoration: none;
                color: white;
                transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
                border: 2px solid #000000;
                position: relative;
                overflow: hidden;
            }}
            
            .link-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
                transition: left 0.5s;
            }}
            
            .link-card:hover::before {{
                left: 100%;
            }}
            
            .link-card:hover {{
                background: #ffffff;
                color: #000000;
                border: 2px solid #000000;
                transform: translateY(-8px);
                box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.3);
            }}
            
            .link-card h3 {{
                margin-bottom: 12px;
                font-size: 1.3em;
                font-weight: 600;
                letter-spacing: -0.5px;
            }}
            
            .link-card p {{
                opacity: 0.85;
                font-size: 0.95em;
                font-weight: 300;
                line-height: 1.6;
            }}
            
            .link-card:hover p {{
                opacity: 0.7;
            }}
            
            .version {{
                text-align: center;
                color: #999999;
                margin-top: 60px;
                font-size: 0.85em;
                font-weight: 300;
                padding-top: 40px;
                border-top: 1px solid #e0e0e0;
            }}
            
            .version p {{
                margin: 5px 0;
            }}
            
            @media (max-width: 768px) {{
                .links {{
                    grid-template-columns: 1fr;
                }}
                
                .container {{
                    padding: 50px 30px;
                }}
                
                h1 {{
                    font-size: 2em;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <img src="/logo-header-h200@2x.png" alt="CREATESONLINE" class="logo">
            <h1>AI-Native Web Framework</h1>
            
            <div class="links">
                <a href="https://createsonline.com/docs" class="link-card">
                    <h3>Documentation</h3>
                    <p>Complete guides and API reference</p>
                </a>
                
                <a href="https://createsonline.com/guide" class="link-card">
                    <h3>Quick Start</h3>
                    <p>Get started in 5 minutes</p>
                </a>
                
                <a href="https://createsonline.com/examples" class="link-card">
                    <h3>Examples</h3>
                    <p>Real-world code examples</p>
                </a>
                
                <a href="https://github.com/meahmedh/createsonline" class="link-card">
                    <h3>GitHub</h3>
                    <p>View source and contribute</p>
                </a>
            </div>
            
            <div class="version">
                <p>CREATESONLINE v0.1.0</p>
                <p>Built by the CREATESONLINE Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Return HTML directly as string
    return html

@app.get("/admin")
async def admin_login(request):
    """Admin login page"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Login - CREATESONLINE</title>
        
        <!-- Favicons -->
        <link rel="icon" type="image/x-icon" href="/favicon.ico">
        <link rel="icon" type="image/png" sizes="32x32" href="/icons/icon-32x32.png">
        
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #000000 0%, #1a1a1a 50%, #000000 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
                position: relative;
                overflow: hidden;
            }}
            
            body::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: repeating-linear-gradient(
                    0deg,
                    transparent,
                    transparent 2px,
                    rgba(255, 255, 255, 0.03) 2px,
                    rgba(255, 255, 255, 0.03) 4px
                );
                animation: scan 8s linear infinite;
                pointer-events: none;
            }}
            
            @keyframes scan {{
                0% {{ transform: translateY(0); }}
                100% {{ transform: translateY(50px); }}
            }}
            
            .login-container {{
                background: rgba(255, 255, 255, 0.98);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(0, 0, 0, 0.1);
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                padding: 60px 50px;
                max-width: 480px;
                width: 100%;
                animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
                position: relative;
                z-index: 1;
            }}
            
            @keyframes slideUp {{
                from {{
                    opacity: 0;
                    transform: translateY(30px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .logo {{
                display: block;
                margin: 0 auto 40px;
                max-width: 280px;
                width: 100%;
                height: auto;
                filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
            }}
            
            h1 {{
                font-size: 2em;
                color: #000000;
                margin-bottom: 10px;
                text-align: center;
                font-weight: 300;
                letter-spacing: -0.5px;
            }}
            
            h1::after {{
                content: '';
                display: block;
                width: 40px;
                height: 2px;
                background: #000000;
                margin: 15px auto 0;
            }}
            
            .subtitle {{
                text-align: center;
                color: #666666;
                font-size: 0.95em;
                margin-bottom: 45px;
                font-weight: 300;
                line-height: 1.6;
            }}
            
            .form-group {{
                margin-bottom: 30px;
                position: relative;
            }}
            
            label {{
                display: block;
                color: #000000;
                font-size: 0.85em;
                margin-bottom: 10px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            input[type="text"],
            input[type="password"] {{
                width: 100%;
                padding: 15px 18px;
                border: 2px solid #e0e0e0;
                background: #ffffff;
                font-size: 1em;
                transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                font-family: inherit;
                color: #000000;
            }}
            
            input[type="text"]:focus,
            input[type="password"]:focus {{
                outline: none;
                background: #fafafa;
                border-color: #000000;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }}
            
            button {{
                width: 100%;
                padding: 18px;
                background: #000000;
                color: white;
                border: 2px solid #000000;
                font-size: 1em;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                text-transform: uppercase;
                letter-spacing: 1.5px;
                font-family: inherit;
                margin-top: 10px;
                position: relative;
                overflow: hidden;
            }}
            
            button::before {{
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
                transition: left 0.5s;
            }}
            
            button:hover::before {{
                left: 100%;
            }}
            
            button:hover {{
                background: #ffffff;
                color: #000000;
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
            }}
            
            button:active {{
                transform: translateY(0);
            }}
            
            .back-link {{
                text-align: center;
                margin-top: 35px;
                padding-top: 30px;
                border-top: 1px solid #e0e0e0;
            }}
            
            .back-link a {{
                color: #666666;
                text-decoration: none;
                font-size: 0.9em;
                transition: all 0.3s ease;
                font-weight: 300;
            }}
            
            .back-link a:hover {{
                color: #000000;
            }}
            
            @media (max-width: 480px) {{
                .login-container {{
                    padding: 40px 30px;
                }}
                
                h1 {{
                    font-size: 1.6em;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="login-container">
            <img src="/logo-header-h200@2x.png" alt="CREATESONLINE" class="logo">
            <h1>Admin Login</h1>
            <p class="subtitle">Enter your credentials to access the admin panel</p>
            
            <form method="POST" action="/admin/login">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <button type="submit">Sign In</button>
            </form>
            
            <div class="back-link">
                <a href="/">Back to Home</a>
            </div>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    import os
    from createsonline.server import run_server
    
    # Load environment variables from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "1") == "1"  # Auto-reload in development
    
    run_server(app, host=host, port=port, reload=reload)
'''
        
        Path("main.py").write_text(basic_app, encoding='utf-8')
        self._success("Created basic main.py application file")


# ========================================
# MAIN CLI ENTRY POINTS
# ========================================

async def main():
    """Main CLI entry point - handles natural language input"""
    
    # Initialize CLI
    cli = CreatesonlineNaturalLanguageCLI()
    
    # Handle command line arguments
    if len(sys.argv) == 1:
        # No arguments - show help
        await cli.handle_help({})
        return
    
    # Join all arguments as natural language input
    user_input = " ".join(sys.argv[1:])
    
    # Handle traditional CLI commands first
    first_arg = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    
    if first_arg == "serve":
        # Traditional serve command
        port = 8000
        if len(sys.argv) > 2 and sys.argv[2].isdigit():
            port = int(sys.argv[2])
        await cli.handle_start_server({"port": port})
        return
    
    if first_arg == "dev":
        # Traditional dev command  
        port = 8000
        if len(sys.argv) > 2 and sys.argv[2].isdigit():
            port = int(sys.argv[2])
        await cli.handle_start_server({"port": port})
        return
    
    if first_arg == "prod":
        # Traditional production command
        workers = 4
        if len(sys.argv) > 2 and sys.argv[2].isdigit():
            workers = int(sys.argv[2])
        await cli.handle_production_server({"workers": workers})
        return
    
    if first_arg == "new":
        # Traditional new project command
        project_name = sys.argv[2] if len(sys.argv) > 2 else "myproject"
        await cli.handle_create_project({"name": project_name})
        return
    
    if first_arg == "init":
        # Initialize project structure
        await cli.handle_init_project({})
        return
    
    if first_arg == "createsuperuser":
        # Traditional superuser command
        await cli.handle_create_superuser({})
        return
    
    if first_arg == "shell":
        # Traditional shell command
        await cli.handle_shell({})
        return
    
    # Handle special cases
    if user_input in ["--help", "-h", "help"]:
        await cli.handle_help({})
        return
    
    if user_input in ["--version", "-v", "version"]:
        await cli.handle_version({})
        return
    
    # Parse natural language
    command_name, params = cli.parse_natural_language(user_input)
    
    if command_name:
        # Execute parsed command
        success = await cli.execute_command(command_name, params)
        
        if success:
            cli._success("Command completed successfully!")
        else:
            cli._error("Command execution failed")
            sys.exit(1)
    else:
        # Unknown command - show suggestions
        cli._warning(f"I didn't understand: '{user_input}'")
        cli._info("Try something like:")
        cli._info('  createsonline "create new project called myapp"')
        cli._info('  createsonline "start development server"')
        cli._info('  createsonline "show framework info"')
        cli._info('  createsonline help')
        sys.exit(1)


def run_cli():
    """Synchronous CLI runner"""
    try:
        if sys.version_info >= (3, 7):
            asyncio.run(main())
        else:
            # Fallback for older Python versions
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nâš ï¸ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] CLI Error: {e}")
        sys.exit(1)


# ========================================
# LEGACY COMMAND SUPPORT (Optional)
# ========================================

def serve(
    port: int = 8000,
    host: str = "127.0.0.1",
    reload: bool = True,
    workers: int = 1
):
    """Legacy serve command for backward compatibility"""
    print("ðŸ”„ Converting to natural language...")
    cmd = f"start development server on port {port}"
    sys.argv = ["createsonline", cmd]
    run_cli()


def dev(port: int = 8000, host: str = "127.0.0.1"):
    """Legacy dev command"""
    serve(port=port, host=host, reload=True)


def prod(port: int = 8000, workers: int = 4):
    """Legacy production command"""
    cmd = f"start production server with {workers} workers"
    sys.argv = ["createsonline", cmd]
    run_cli()


def new(project_name: str, ai: bool = True, admin: bool = True, auth: bool = True):
    """Legacy new project command"""
    features = []
    if ai:
        features.append("with ai features")
    if admin:
        features.append("with admin")
    if auth:
        features.append("with auth")
    
    cmd = f"create new project called {project_name} {' '.join(features)}"
    sys.argv = ["createsonline", cmd]
    run_cli()


def info():
    """Legacy info command"""
    sys.argv = ["createsonline", "show framework info"]
    run_cli()


def version():
    """Legacy version command"""
    sys.argv = ["createsonline", "version"]
    run_cli()


def shell():
    """Legacy shell command"""
    sys.argv = ["createsonline", "shell"]
    run_cli()


def createsuperuser():
    """Legacy createsuperuser command"""
    sys.argv = ["createsonline", "create superuser"]
    run_cli()


# ========================================
# TYPER APP FALLBACK (If Available)
# ========================================

if TYPER_AVAILABLE:
    # Create Typer app for advanced users who prefer traditional CLI
    typer_app = typer.Typer(
        name="createsonline",
        help="CREATESONLINE Framework - Natural Language CLI",
        add_completion=False,
        rich_markup_mode="rich",
        no_args_is_help=True
    )
    
    # Add legacy commands to Typer app
    typer_app.command("serve")(serve)
    typer_app.command("dev")(dev)
    typer_app.command("prod")(prod)
    typer_app.command("new")(new)
    typer_app.command("info")(info)
    typer_app.command("version")(version)
    typer_app.command("shell")(shell)
    typer_app.command("createsuperuser")(createsuperuser)
    
    # Main command that handles natural language
    @typer_app.callback(invoke_without_command=True)
    def main_callback(
        ctx,  # FIXED: Remove type annotation to avoid stub issues
        natural_command: str = typer.Argument(None, help="Natural language command")
    ):
        """
        ï¼£âŽ¯â— CREATESONLINE Natural Language CLI
        
        Express your intent naturally:
        createsonline "create new AI-powered project called blog"
        createsonline "start development server on port 8000"
        """
        if ctx.invoked_subcommand is None:
            if natural_command:
                sys.argv = ["createsonline", natural_command]
                run_cli()
            else:
                # Show help
                sys.argv = ["createsonline", "help"]
                run_cli()
    
    # Export the Typer app
    app = typer_app

else:
    # No Typer available - use our internal implementation
    app = None


# ========================================
# MODULE EXPORTS
# ========================================

__all__ = [
    'main',
    'run_cli',
    'CreatesonlineNaturalLanguageCLI',
    'serve',
    'dev', 
    'prod',
    'new',
    'info',
    'version',
    'shell',
    'createsuperuser'
]

# Entry point for console scripts
if __name__ == "__main__":
    run_cli()


