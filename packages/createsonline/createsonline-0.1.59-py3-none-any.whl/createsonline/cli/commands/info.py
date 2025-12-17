# createsonline/cli/commands/info.py
"""
CREATESONLINE Info Commands

Provides info and version commands.
"""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
import sys
import platform

console = Console()

def info_command():
    """ Show comprehensive framework information"""
    
    # Get framework info
    try:
        import createsonline
        framework_info = createsonline.get_framework_info()
        ai_available = True
        try:
            import createsonline.ai
            ai_info = createsonline.ai.get_ai_info()
        except:
            ai_available = False
            ai_info = {}
    except ImportError:
        framework_info = {
            "name": "CREATESONLINE",
            "version": "0.1.0",
            "tagline": "Build Intelligence Into Everything"
        }
        ai_available = False
        ai_info = {}
    
    # Framework banner
    banner = Panel(
        f"[bold blue]{framework_info.get('name', 'CREATESONLINE')}[/bold blue]\n"
        f"[cyan]{framework_info.get('tagline', 'Build Intelligence Into Everything')}[/cyan]\n\n"
        f"[green]Version:[/green] {framework_info.get('version', '0.1.0')}\n"
        f"[green]Python:[/green] {sys.version.split()[0]}\n"
        f"[green]Platform:[/green] {platform.system()} {platform.release()}",
        title="Ｃ⎯● Framework Information",
        border_style="blue"
    )
    
    # Features table
    features_table = Table(title="✨ Framework Features", show_header=False)
    features_table.add_column("Feature", style="cyan")
    features_table.add_column("Status", style="green")
    
    features = framework_info.get('features', [
        "Pure AI-Native Architecture",
        "Built-in Admin Interface", 
        "User Management System",
        "AI-Enhanced ORM",
        "Natural Language Queries",
        "Vector Similarity Search",
        "LLM Integration",
        "Beautiful CLI Tools"
    ])
    
    for feature in features:
        features_table.add_row(f"• {feature}", " Available")
    
    # AI info table
    ai_table = Table(title="Ｃ⎯● AI Capabilities", show_header=False)
    ai_table.add_column("Capability", style="cyan")
    ai_table.add_column("Status", style="green" if ai_available else "yellow")
    
    if ai_available and ai_info:
        field_types = ai_info.get('field_types', [])
        services = ai_info.get('services', [])
        capabilities = ai_info.get('capabilities', [])
        
        ai_table.add_row("AI Module", " Available" if ai_available else " Limited")
        ai_table.add_row(f"Field Types", f" {len(field_types)} types")
        ai_table.add_row(f"AI Services", f" {len(services)} services") 
        ai_table.add_row(f"Capabilities", f" {len(capabilities)} features")
    else:
        ai_table.add_row("AI Module", " Limited Mode")
        ai_table.add_row("Field Types", " Basic support")
        ai_table.add_row("AI Services", " Mock services")
        ai_table.add_row("Capabilities", " Reduced functionality")
    
    # Dependencies table
    deps_table = Table(title="📦 Core Dependencies", show_header=False)
    deps_table.add_column("Package", style="cyan")
    deps_table.add_column("Status", style="green")
    
    core_deps = [
        ("uvicorn", "ASGI Server"),
        ("sqlalchemy", "Database ORM"),
        ("typer", "CLI Framework"),
        ("rich", "Terminal UI"),
        ("pydantic", "Data Validation")
    ]
    
    for pkg, desc in core_deps:
        try:
            __import__(pkg)
            status = " Installed"
        except ImportError:
            status = " Missing"
        deps_table.add_row(f"{pkg} ({desc})", status)
    
    # Display everything
    console.print(banner)
    console.print("\n")
    
    # Show tables in columns
    console.print(Columns([features_table, ai_table]))
    console.print("\n")
    console.print(deps_table)
    
    # Commands info
    commands_info = Panel(
        "[bold green]Available Commands:[/bold green]\n\n"
        "[cyan]createsonline serve[/cyan] - Start development server\n"
        "[cyan]createsonline dev[/cyan] - Development mode with auto-reload\n" 
        "[cyan]createsonline prod[/cyan] - Production server\n"
        "[cyan]createsonline new[/cyan] - Create new project\n"
        "[cyan]createsonline info[/cyan] - Show this information\n"
        "[cyan]createsonline version[/cyan] - Show version\n"
        "[cyan]createsonline shell[/cyan] - Interactive shell\n"
        "[cyan]createsonline createsuperuser[/cyan] - Create admin user",
        title=" CLI Commands",
        border_style="green"
    )
    console.print(commands_info)

def version_command():
    """📦 Show version information"""
    
    try:
        import createsonline
        version = createsonline.__version__
        name = createsonline.__framework_name__
        tagline = createsonline.__tagline__
    except ImportError:
        version = "0.1.0"
        name = "CREATESONLINE"
        tagline = "Build Intelligence Into Everything"
    
    # Version banner
    version_panel = Panel(
        f"[bold blue]{name}[/bold blue] [bold white]{version}[/bold white]\n\n"
        f"[cyan]{tagline}[/cyan]\n\n"
        f"[green]Python:[/green] {sys.version.split()[0]}\n"
        f"[green]Platform:[/green] {platform.system()}\n"
        f"[green]Architecture:[/green] {platform.machine()}",
        title="📦 Version Information",
        border_style="blue"
    )
    
    console.print(version_panel)
    
    # Show Python and system info
    sys_table = Table(title="🖥 System Information", show_header=False)
    sys_table.add_column("Property", style="cyan")
    sys_table.add_column("Value", style="white")
    
    sys_table.add_row("Python Version", sys.version.split()[0])
    sys_table.add_row("Python Path", sys.executable)
    sys_table.add_row("Platform", f"{platform.system()} {platform.release()}")
    sys_table.add_row("Machine", platform.machine())
    sys_table.add_row("Processor", platform.processor() or "Unknown")
    
    console.print("\n")
    console.print(sys_table)