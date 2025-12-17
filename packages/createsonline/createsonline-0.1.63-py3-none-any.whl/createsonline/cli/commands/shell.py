# createsonline/cli/commands/shell.py
"""
CREATESONLINE Interactive Shell

Launch an interactive Python shell with CREATESONLINE imports.
"""
from rich.console import Console

console = Console()

def shell_command():
    """🐚 Interactive CREATESONLINE shell with pre-loaded imports"""
    
    console.print("🐚 [bold blue]CREATESONLINE Interactive Shell[/bold blue]")
    console.print("[cyan]Pre-loaded imports available:[/cyan]")
    console.print("  • [yellow]createsonline[/yellow] - Main framework")
    console.print("  • [yellow]createsonline.ai[/yellow] - AI capabilities") 
    console.print("  • [yellow]app[/yellow] - Application instance (if main.py exists)")
    console.print("  • [yellow]models[/yellow] - Database models (if available)")
    console.print()
    
    # Prepare the shell environment
    import sys
    import os
    
    # Try to import createsonline
    shell_globals = {}
    shell_locals = {}
    
    try:
        import createsonline
        shell_globals['createsonline'] = createsonline
        console.print(" [green]createsonline imported[/green]")
    except ImportError:
        console.print(" [yellow]createsonline not available[/yellow]")
    
    try:
        import createsonline.ai as ai
        shell_globals['ai'] = ai
        console.print(" [green]createsonline.ai imported[/green]")
    except ImportError:
        console.print(" [yellow]createsonline.ai not available[/yellow]")
    
    # Try to import app from main.py
    if os.path.exists("main.py"):
        try:
            sys.path.insert(0, os.getcwd())
            import main
            if hasattr(main, 'app'):
                shell_globals['app'] = main.app
                console.print(" [green]app imported from main.py[/green]")
        except Exception as e:
            console.print(f" [yellow]Could not import app: {e}[/yellow]")
    
    # Try to import models
    if os.path.exists("models"):
        try:
            import models
            shell_globals['models'] = models
            console.print(" [green]models imported[/green]")
        except Exception:
            pass
    
    # Common imports
    shell_globals.update({
        'os': os,
        'sys': sys,
        'Path': __import__('pathlib').Path,
        'json': __import__('json'),
        'asyncio': __import__('asyncio'),
    })
    
    console.print()
    console.print("[dim]Type 'exit()' or Ctrl+D to quit[/dim]")
    console.print()
    
    # Launch the shell
    try:
        # Try IPython first (better experience)
        try:
            from IPython import start_ipython
            start_ipython(argv=[], user_ns=shell_globals)
        except ImportError:
            # Fallback to standard Python shell
            import code
            code.interact(
                banner="Python shell with CREATESONLINE",
                local=shell_globals
            )
    except (EOFError, KeyboardInterrupt):
        console.print("\n[yellow]Shell session ended[/yellow]")
    except Exception as e:
        console.print(f"[red]Shell error: {e}[/red]")