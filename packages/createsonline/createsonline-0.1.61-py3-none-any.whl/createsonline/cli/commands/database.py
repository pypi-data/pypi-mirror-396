# createsonline/cli/commands/database.py
"""
CREATESONLINE Database Commands

Database management and AI query commands for the CLI.
Provides natural language database querying and audit capabilities.
"""

import json
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Internal console implementation (fallback for rich)
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.syntax import Syntax
    from rich.prompt import Confirm
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    # Internal console fallback
    class SimpleConsole:
        def print(self, text, **kwargs):
            if isinstance(text, str):
                import logging as _logging; _logging.getLogger("createsonline.cli.database").info(text)
            else:
                import logging as _logging; _logging.getLogger("createsonline.cli.database").info(str(text))
        
        def input(self, prompt):
            return input(prompt)
    
    console = SimpleConsole()


def db_ai_query_command(
    prompt: str,
    approve: bool = False,
    explain: bool = False,
    save: str = None,
    output_format: str = "table"
):
    """ðŸ¤– AI-powered natural language database queries
    
    Examples:
        createsonline db ai-query "show last 10 users"
        createsonline db ai-query "how many active users" --approve
        createsonline db ai-query "list admin users" --explain
        createsonline db ai-query "recent error logs" --save recent-errors
    """
    
    try:
        # Import database assistant - use the main database.py file
        import os
        import importlib.util
        
        # Get the path to the main database.py file  
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(current_dir, 'database.py')
        
        # Load the database module
        spec = importlib.util.spec_from_file_location("database_main", db_path)
        db_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(db_module)
        
        # Load the assistant module
        assistant_path = os.path.join(current_dir, 'database', 'assistant.py')
        spec = importlib.util.spec_from_file_location("assistant", assistant_path)
        assistant_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(assistant_module)
        
        # Initialize database and assistant
        db = db_module.get_database()
        assistant = assistant_module.create_assistant(db)
        
        if RICH_AVAILABLE:
            console.print(Panel(
                f"[bold blue]ðŸ¤– CREATESONLINE Database AI Assistant[/bold blue]\n"
                f"[cyan]Natural Language â†’ SQL Query[/cyan]\n\n"
                f"[green]Prompt:[/green] {prompt}\n"
                f"[green]Safety:[/green] SELECT-only mode\n"
                f"[green]Audit:[/green] All queries logged",
                title="ðŸ—„ï¸ Database AI Query",
                border_style="blue"
            ))
        else:
            console.print("CREATESONLINE Database AI Assistant") if RICH_AVAILABLE else __import__("logging").getLogger("createsonline.cli.database").info("CREATESONLINE Database AI Assistant")
            (console.print(f"Prompt: {prompt}") if RICH_AVAILABLE else __import__("logging").getLogger("createsonline.cli.database").info(f"Prompt: {prompt}"))
        # Handle explain mode
        if explain:
            try:
                parsed = assistant.parse_natural_language(prompt)
                _display_explanation(parsed)
                return
            except Exception as e:
                if RICH_AVAILABLE:
                    console.print(f"[red]âŒ Failed to parse query: {e}[/red]")
                else:
                __import__("logging").getLogger("createsonline.cli.database").error(f"Failed to parse query: {e}")
                return
        
        # Parse and generate SQL
        try:
            parsed_query = assistant.parse_natural_language(prompt)
            sql = assistant.generate_sql(parsed_query)
            
            # Create result structure
            result = {
                'success': True,
                'sql': sql,
                'parsed_query': parsed_query,
                'prompt': prompt
            }
            
        except Exception as e:
            result = {
                'success': False,
                'error': str(e),
                'prompt': prompt
            }
            _display_error(result)
            return
        
        # Ask for confirmation if not auto-approved
        if not approve and not _confirm_execution(result):
            console.print("âŒ Query cancelled by user")
            return
        
        # Execute the query
        try:
            query_results = assistant.execute_safe(result['sql'], result['parsed_query'])
            result['data'] = query_results.get('results', [])
            result['rows_affected'] = len(result['data'])
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            _display_error(result)
            return
        
        # Display results
        _display_results(result, output_format)
        
        # Save as reusable command if requested
        if save:
            _save_command(save, prompt, result)
            
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[red]âŒ Database AI Query Error: {e}[/red]")
        else:
            __import__("logging").getLogger("createsonline.cli.database").error(f"Database AI Query Error: {e}")
def db_rollback_command(audit_id: int = None, last: bool = False, dry_run: bool = False):
    """ðŸ”„ Rollback database operations using audit logs
    
    Examples:
        createsonline db rollback --last
        createsonline db rollback --id 42
        createsonline db rollback --last --dry-run
    """
    
    try:
        from ...database.assistant import create_assistant
        from ...database import get_database
        
        db = get_database()
        assistant = create_assistant(db)
        
        if RICH_AVAILABLE:
            console.print(Panel(
                "[bold yellow]ðŸ”„ Database Rollback Assistant[/bold yellow]\n"
                "[orange]Undo database operations safely[/orange]",
                title="ðŸ—„ï¸ Database Rollback",
                border_style="yellow"
            ))
        else:
            __import__("logging").getLogger("createsonline.cli.database").info("Database Rollback Assistant")
        # Get audit entries to rollback
        if last:
            recent_queries = assistant.get_recent_queries(1)
            if not recent_queries:
                console.print("âŒ No recent queries found")
                return
            audit_entry = recent_queries[0]
        elif audit_id:
            # TODO: Implement get_audit_by_id
            console.print("âŒ Rollback by ID not yet implemented")
            return
        else:
            console.print("âŒ Must specify either --last or --id")
            return
        
        # Display what would be rolled back
        _display_rollback_preview(audit_entry)
        
        if dry_run:
            console.print("âœ… Dry-run complete - no changes made")
            return
        
        # Confirm rollback
        if not Confirm.ask("Proceed with rollback?") if RICH_AVAILABLE else input("Proceed with rollback? (y/N): ").lower().startswith('y'):
            console.print("âŒ Rollback cancelled")
            return
        
        # For now, only log the rollback intent (actual rollback logic would be complex)
        console.print("âš ï¸ Rollback functionality is logged but not yet implemented")
        console.print("This is a safety feature - manual review recommended")
        
    except Exception as e:
        console.print(f"âŒ Rollback Error: {e}")


def db_audit_log_command(limit: int = 20, filter_type: str = None):
    """ðŸ“‹ View database operation audit logs
    
    Examples:
        createsonline db audit-log
        createsonline db audit-log --limit 50
        createsonline db audit-log --filter-type error
    """
    
    try:
        from ...database.assistant import create_assistant
        from ...database import get_database
        
        db = get_database()
        assistant = create_assistant(db)
        
        if RICH_AVAILABLE:
            console.print(Panel(
                "[bold green]ðŸ“‹ Database Audit Log[/bold green]\n"
                "[cyan]Recent database operations[/cyan]",
                title="ðŸ—„ï¸ Audit Log",
                border_style="green"
            ))
        else:
        __import__("logging").getLogger("createsonline.cli.database").info("Database Audit Log")
        # Get recent queries
        recent_queries = assistant.get_recent_queries(limit)
        
        if not recent_queries:
            console.print("â„¹ï¸ No audit log entries found")
            return
        
        # Filter if requested
        if filter_type:
            recent_queries = [q for q in recent_queries if q.get('status') == filter_type]
        
        # Display audit log
        _display_audit_log(recent_queries)
        
    except Exception as e:
        console.print(f"âŒ Audit Log Error: {e}")


def _display_explanation(parsed_query: Dict[str, Any]):
    """Display query explanation"""
    if RICH_AVAILABLE:
        # Create explanation panel
        explanation_content = f"""
[yellow]Original Prompt:[/yellow] {parsed_query['original_prompt']}

[yellow]Query Type:[/yellow] {parsed_query['query_type'].value.upper()}
[yellow]Target Table:[/yellow] {parsed_query['table']}
[yellow]Safety Level:[/yellow] {parsed_query['safety_level'].value}
[yellow]Columns:[/yellow] {', '.join(parsed_query['columns'])}

[yellow]Conditions:[/yellow] {len(parsed_query['conditions'])} conditions
[yellow]Limit:[/yellow] {parsed_query.get('limit', 'None')}
[yellow]Order By:[/yellow] {parsed_query.get('order_by', 'None')}
"""
        
        console.print(Panel(
            explanation_content,
            title="ðŸ” Query Explanation",
            border_style="yellow"
        ))
    else:
        __import__("logging").getLogger("createsonline.cli.database").info(f"Prompt: {parsed_query['original_prompt']}")
        __import__("logging").getLogger("createsonline.cli.database").info(f"Query Type: {parsed_query['query_type'].value}")
        __import__("logging").getLogger("createsonline.cli.database").info(f"Target Table: {parsed_query['table']}")
        __import__("logging").getLogger("createsonline.cli.database").info(f"Safety Level: {parsed_query['safety_level'].value}")
        console.print(Panel(
            explanation_content,
            title="ðŸ” Query Explanation",
            border_style="yellow"
        ))


def _display_error(result: Dict[str, Any]):
    """Display error information"""
    if RICH_AVAILABLE:
        console.print(Panel(
            f"[red]Error: {result['error']}[/red]\n"
            f"[yellow]Prompt: {result['prompt']}[/yellow]",
            title="âŒ Query Failed",
            border_style="red"
        ))
    else:
        __import__("logging").getLogger("createsonline.cli.database").error(f"Error: {result['error']}")
        __import__("logging").getLogger("createsonline.cli.database").info(f"Prompt: {result['prompt']}" )
def _confirm_execution(result: Dict[str, Any]) -> bool:
    """Ask user to confirm query execution"""
    if not RICH_AVAILABLE:
        response = input(f"Execute SQL: {result.get('sql', 'Unknown')}? (y/N): ")
        return response.lower().startswith('y')
    
    # Display query preview
    sql = result.get('sql', 'Unknown')
    
    console.print(Panel(
        f"[yellow]Generated SQL:[/yellow]\n{sql}\n\n"
        f"[cyan]This query will be executed against your database.[/cyan]",
        title="ðŸ” Confirm Execution",
        border_style="yellow"
    ))
    
    return Confirm.ask("Execute this query?")


def _display_results(result: Dict[str, Any], output_format: str):
    """Display query results in specified format"""
    data = result['data']
    
    if output_format == "json":
        __import__("logging").getLogger("createsonline.cli.database").info(json.dumps(data, indent=2, default=str))
        return
    
    if not data:
        console.print("â„¹ï¸ No results found")
        return
    
    if RICH_AVAILABLE and output_format == "table":
        # Create rich table
        table = Table(title=f"Query Results ({len(data)} rows)")
        
        # Add columns based on first row
        if data and isinstance(data[0], dict):
            for column in data[0].keys():
                table.add_column(str(column), style="cyan")
            
            # Add rows
            for row in data:
                table.add_row(*[str(value) for value in row.values()])
        
        console.print(table)
        
        # Show execution info
        console.print(f"\nâœ… Query executed successfully")
        console.print(f"ðŸ“Š Rows returned: {result['rows_returned']}")
        console.print(f"â±ï¸ Execution time: {result['execution_time']}")
    else:
        # Simple text output
        console.print(f"Results ({len(data)} rows):") if RICH_AVAILABLE else __import__("logging").getLogger("createsonline.cli.database").info(f"Results ({len(data)} rows):")
        for i, row in enumerate(data):
            console.print(f"Row {i+1}: {row}") if RICH_AVAILABLE else __import__("logging").getLogger("createsonline.cli.database").info(f"Row {i+1}: {row}")
        __import__("logging").getLogger("createsonline.cli.database").info(f"Query executed successfully - {result['rows_returned']} rows")
def _display_rollback_preview(audit_entry: Dict[str, Any]):
    """Display rollback preview"""
    if RICH_AVAILABLE:
        preview_content = f"""
[yellow]Operation to Rollback:[/yellow]
[white]Timestamp:[/white] {audit_entry.get('timestamp', 'Unknown')}
[white]Original Prompt:[/white] {audit_entry.get('original_prompt', 'N/A')}
[white]SQL Query:[/white] {audit_entry.get('sql_query', 'Unknown')}
[white]Status:[/white] {audit_entry.get('status', 'Unknown')}
[white]Rows Affected:[/white] {audit_entry.get('rows_affected', 0)}

[red]âš ï¸ Rollback operations are complex and may not be reversible.[/red]
[red]Manual verification is strongly recommended.[/red]
"""
        
        console.print(Panel(
            preview_content,
            title="ðŸ”„ Rollback Preview",
            border_style="yellow"
        ))
    else:
        console.print("Operation to Rollback:") if RICH_AVAILABLE else __import__("logging").getLogger("createsonline.cli.database").info("Operation to Rollback:")
        pass
        pass
        pass
def _display_audit_log(entries: List[Dict[str, Any]]):
    """Display audit log entries"""
    if RICH_AVAILABLE:
        table = Table(title=f"Database Audit Log ({len(entries)} entries)")
        table.add_column("Timestamp", style="cyan")
        table.add_column("Prompt", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Rows", style="blue")
        table.add_column("Error", style="red")
        
        for entry in entries:
            table.add_row(
                str(entry.get('timestamp', 'Unknown'))[:19],  # Truncate timestamp
                str(entry.get('original_prompt', 'N/A'))[:50] + ('...' if len(str(entry.get('original_prompt', ''))) > 50 else ''),
                str(entry.get('status', 'Unknown')),
                str(entry.get('rows_affected', 0)),
                str(entry.get('error_message', ''))[:30] + ('...' if len(str(entry.get('error_message', ''))) > 30 else '')
            )
        
        console.print(table)
    else:
        __import__("logging").getLogger("createsonline.cli.database").info(f"Audit Log ({len(entries)} entries):")
        for i, entry in enumerate(entries):
            __import__("logging").getLogger("createsonline.cli.database").info(f"{i+1}. {entry.get('timestamp', 'Unknown')} - {entry.get('original_prompt', 'N/A')} [{entry.get('status', 'Unknown')}]")
def _save_command(name: str, prompt: str, result: Dict[str, Any]):
    """Save successful query as reusable CLI command"""
    # TODO: Implement command saving to config file
    console.print(f"ðŸ’¾ Command saving not yet implemented")
    console.print(f"Would save: '{name}' -> '{prompt}'")



