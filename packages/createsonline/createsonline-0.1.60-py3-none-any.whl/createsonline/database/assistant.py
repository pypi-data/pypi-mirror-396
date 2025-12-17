# createsonline/database/assistant.py
"""
CREATESONLINE Database Assistant - AI-Powered SQL Generation

Converts natural language prompts into safe SQLAlchemy queries.
Focuses on SELECT operations with strict safety guards against destructive operations.

Features:
- Natural language → SQLAlchemy object conversion
- Safety filters for destructive operations
- Audit logging for all operations
- Rollback capabilities

Usage:
    assistant = DatabaseAssistant(db_connection)
    query = assistant.generate_query("show last 10 error logs")
    result = assistant.execute_safe(query)
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
import json

# Core imports - using absolute imports to avoid relative import issues
try:
    from createsonline.database import DatabaseConnection
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    
    import importlib.util
    db_spec = importlib.util.spec_from_file_location(
        "database_connection", 
        os.path.join(os.path.dirname(__file__), '..', 'database.py')
    )
    db_module = importlib.util.module_from_spec(db_spec)
    db_spec.loader.exec_module(db_module)
    DatabaseConnection = db_module.DatabaseConnection

# Setup logging
logger = logging.getLogger("createsonline.database.assistant")

class QueryType(Enum):
    """Supported query types with safety levels"""
    SELECT = "select"      # Always safe
    COUNT = "count"        # Always safe  
    UPDATE = "update"      # Requires confirmation
    INSERT = "insert"      # Requires confirmation
    DELETE = "delete"      # Requires explicit approval
    DROP = "drop"          # Blocked by default
    CREATE = "create"      # Requires confirmation


class SafetyLevel(Enum):
    """Safety levels for different operations"""
    SAFE = "safe"              # No confirmation needed
    CONFIRMATION = "confirm"   # Requires user confirmation
    EXPLICIT = "explicit"      # Requires explicit --allow-destructive flag
    BLOCKED = "blocked"        # Always blocked


class DatabaseAssistant:
    """AI-powered database query assistant with safety controls"""
    
    def __init__(self, db, safety_mode: str = "strict"):
        self.db = db
        self.safety_mode = safety_mode
        
        # Safety mappings
        self.safety_map = {
            QueryType.SELECT: SafetyLevel.SAFE,
            QueryType.COUNT: SafetyLevel.SAFE,
            QueryType.UPDATE: SafetyLevel.CONFIRMATION,
            QueryType.INSERT: SafetyLevel.CONFIRMATION,
            QueryType.DELETE: SafetyLevel.EXPLICIT,
            QueryType.DROP: SafetyLevel.BLOCKED,
            QueryType.CREATE: SafetyLevel.CONFIRMATION
        }
        
        # Natural language patterns for different query types
        self.nl_patterns = {
            QueryType.DROP: [
                r'\b(drop)\b.*\b(table|database|index)\b',
                r'\b(drop table|drop database|drop index)\b'
            ],
            QueryType.DELETE: [
                r'\b(delete)\b.*\b(from|users?|records?|entries?)\b',
                r'\b(remove|drop)\b.*\b(user|record|entry)\b'
            ],
            QueryType.UPDATE: [
                r'\b(update)\b.*\b(set|users?|records?)\b',
                r'\b(modify|change|set)\b.*\b(password|email|status)\b',
                r'\b(make|turn)\b.*\b(active|inactive)\b'
            ],
            QueryType.INSERT: [
                r'\b(insert)\b.*\b(into|values?|users?)\b',
                r'\b(add|create|new)\b.*\b(user|record|entry)\b'
            ],
            QueryType.COUNT: [
                r'\bhow many\b',
                r'\bcount\b.*\b(users|records|entries|rows)\b',
                r'\btotal\b.*\b(number|count)\b'
            ],
            QueryType.SELECT: [
                r'\b(show|display|list|get|find|fetch|retrieve)\b',
                r'\b(what|which)\b.*\b(users|records|entries|rows)\b',
                r'\b(last|recent|latest)\b.*\b(\d+)\b',
                r'\bselect\b'
            ]
        }
        
        # Common table mapping for natural language
        self.table_mapping = {
            'users': 'createsonline_users',
            'user': 'createsonline_users',
            'sessions': 'admin_sessions',
            'session': 'admin_sessions',
            'settings': 'app_settings',
            'setting': 'app_settings',
            'conversations': 'ai_conversations',
            'conversation': 'ai_conversations',
            'logs': 'audit_logs',
            'log': 'audit_logs',
            'errors': 'audit_logs',
            'error': 'audit_logs'
        }
        
        # Common column mapping
        self.column_mapping = {
            'name': 'username',
            'email': 'email',
            'active': 'is_active',
            'staff': 'is_staff',
            'admin': 'is_superuser',
            'created': 'date_joined',
            'joined': 'date_joined',
            'login': 'last_login'
        }

    def parse_natural_language(self, prompt: str) -> Dict[str, Any]:
        """Parse natural language prompt into structured query components"""
        prompt_lower = prompt.lower().strip()
        
        # Detect query type
        query_type = self._detect_query_type(prompt_lower)
        
        # Extract table name
        table_name = self._extract_table_name(prompt_lower)
        
        # Extract conditions
        conditions = self._extract_conditions(prompt_lower)
        
        # Extract limit/order
        limit = self._extract_limit(prompt_lower)
        order_by = self._extract_order(prompt_lower)
        
        # Extract columns (for SELECT)
        columns = self._extract_columns(prompt_lower, query_type)
        
        return {
            'query_type': query_type,
            'table': table_name,
            'columns': columns,
            'conditions': conditions,
            'limit': limit,
            'order_by': order_by,
            'original_prompt': prompt,
            'safety_level': self.safety_map.get(query_type, SafetyLevel.BLOCKED)
        }

    def _detect_query_type(self, prompt: str) -> QueryType:
        """Detect the type of query from natural language"""
        for query_type, patterns in self.nl_patterns.items():
            for pattern in patterns:
                if re.search(pattern, prompt, re.IGNORECASE):
                    return query_type
        
        # Default to SELECT for safety
        return QueryType.SELECT

    def _extract_table_name(self, prompt: str) -> str:
        """Extract table name from natural language"""
        # Look for known table keywords
        for nl_name, db_name in self.table_mapping.items():
            if re.search(rf'\b{re.escape(nl_name)}\b', prompt):
                return db_name
        
        # Default to users table (most common)
        return 'createsonline_users'

    def _extract_conditions(self, prompt: str) -> List[Dict[str, Any]]:
        """Extract WHERE conditions from natural language"""
        conditions = []
        
        # Pattern: "where X is Y" or "with X = Y"
        where_patterns = [
            r'\b(?:where|with)\s+(\w+)\s+(?:is|=|equals?)\s+(["\']?\w+["\']?)',
            r'\b(\w+)\s+(?:is|=|equals?)\s+(["\']?\w+["\']?)',
            r'\bactive\b',  # Special case for is_active = true
            r'\binactive\b',  # Special case for is_active = false
            r'\badmin\b',    # Special case for is_superuser = true
        ]
        
        for pattern in where_patterns:
            matches = re.finditer(pattern, prompt, re.IGNORECASE)
            for match in matches:
                if 'active' in match.group().lower():
                    conditions.append({
                        'column': 'is_active',
                        'operator': '=',
                        'value': not ('inactive' in match.group().lower())
                    })
                elif 'admin' in match.group().lower():
                    conditions.append({
                        'column': 'is_superuser',
                        'operator': '=',
                        'value': True
                    })
                elif match.groups() and len(match.groups()) >= 2:
                    column = self.column_mapping.get(match.group(1), match.group(1))
                    value = match.group(2).strip('"\'')
                    conditions.append({
                        'column': column,
                        'operator': '=',
                        'value': value
                    })
        
        return conditions

    def _extract_limit(self, prompt: str) -> Optional[int]:
        """Extract LIMIT from natural language"""
        # Pattern: "last 10", "first 5", "limit 20"
        limit_patterns = [
            r'\b(?:last|first|top|limit)\s+(\d+)\b',
            r'\b(\d+)\s+(?:users|records|entries|rows)\b'
        ]
        
        for pattern in limit_patterns:
            match = re.search(pattern, prompt)
            if match:
                return int(match.group(1))
        
        return None

    def _extract_order(self, prompt: str) -> Optional[Dict[str, str]]:
        """Extract ORDER BY from natural language"""
        order_patterns = [
            r'\b(?:order by|sort by)\s+(\w+)\s*(asc|desc)?\b',
            r'\b(newest|latest|recent)\b',  # ORDER BY created DESC
            r'\b(oldest|first)\b',          # ORDER BY created ASC
        ]
        
        for pattern in order_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                if 'newest' in match.group().lower() or 'latest' in match.group().lower() or 'recent' in match.group().lower():
                    return {'column': 'date_joined', 'direction': 'DESC'}
                elif 'oldest' in match.group().lower() or 'first' in match.group().lower():
                    return {'column': 'date_joined', 'direction': 'ASC'}
                else:
                    column = self.column_mapping.get(match.group(1), match.group(1))
                    direction = match.group(2).upper() if len(match.groups()) > 1 and match.group(2) else 'ASC'
                    return {'column': column, 'direction': direction}
        
        return None

    def _extract_columns(self, prompt: str, query_type: QueryType) -> List[str]:
        """Extract columns to select"""
        if query_type == QueryType.COUNT:
            return ['COUNT(*)']
        
        # Look for specific column mentions
        columns = []
        column_patterns = [
            r'\b(username|email|name)\b',
            r'\b(first_name|last_name|full name)\b',
            r'\b(active|status)\b',
            r'\b(admin|superuser)\b',
            r'\b(joined|created|date)\b'
        ]
        
        for pattern in column_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                match = re.search(pattern, prompt, re.IGNORECASE).group()
                mapped_column = self.column_mapping.get(match.lower(), match.lower())
                if mapped_column not in columns:
                    columns.append(mapped_column)
        
        # Default to all columns if none specified
        if not columns:
            columns = ['*']
        
        return columns

    def generate_sql(self, natural_query_or_parsed) -> str:
        """Generate safe SQL from natural language query or parsed query
        
        Args:
            natural_query_or_parsed: Either a string (natural language) or dict (parsed query)
            
        Returns:
            SQL string
        """
        # Handle both string input and parsed dict input
        if isinstance(natural_query_or_parsed, str):
            parsed_query = self.parse_natural_language(natural_query_or_parsed)
        else:
            parsed_query = natural_query_or_parsed
            
        query_type = parsed_query['query_type']
        table = parsed_query['table']
        columns = parsed_query['columns']
        conditions = parsed_query['conditions']
        limit = parsed_query['limit']
        order_by = parsed_query['order_by']
        safety_level = parsed_query['safety_level']
        
        # Safety check - block dangerous operations
        if safety_level == SafetyLevel.BLOCKED:
            raise ValueError(f"Query type {query_type.value} is blocked for safety reasons")
        
        if safety_level in [SafetyLevel.EXPLICIT, SafetyLevel.CONFIRMATION]:
            raise ValueError(f"Query type {query_type.value} requires {safety_level.value} approval")
        
        # Validate table name for safety
        safe_table = self.db._validate_identifier(table)
        
        # Build SQL based on query type
        if query_type in [QueryType.SELECT, QueryType.COUNT]:
            # Build SELECT query
            column_str = ', '.join(columns) if columns != ['*'] else '*'
            sql = f"SELECT {column_str} FROM {safe_table}"
            
            # Add WHERE conditions
            if conditions:
                where_parts = []
                for condition in conditions:
                    safe_column = self.db._validate_identifier(condition['column'])
                    if isinstance(condition['value'], bool):
                        value_str = 'TRUE' if condition['value'] else 'FALSE'
                    elif isinstance(condition['value'], str):
                        value_str = f"'{condition['value']}'"
                    else:
                        value_str = str(condition['value'])
                    
                    where_parts.append(f"{safe_column} {condition['operator']} {value_str}")
                
                sql += " WHERE " + " AND ".join(where_parts)
            
            # Add ORDER BY
            if order_by:
                safe_order_column = self.db._validate_identifier(order_by['column'])
                sql += f" ORDER BY {safe_order_column} {order_by['direction']}"
            
            # Add LIMIT
            if limit:
                sql += f" LIMIT {limit}"
        
        else:
            # For now, only support SELECT queries in safe mode
            raise ValueError(f"Query type {query_type.value} requires explicit approval")
        
        return sql

    def execute_safe(self, sql: str, parsed_query: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute SQL with safety checks and audit logging"""
        
        # Safety check - only allow SELECT statements in safe mode
        sql_upper = sql.strip().upper()
        if not sql_upper.startswith('SELECT'):
            raise ValueError("Only SELECT queries are allowed in safe mode")
        
        # Log the query attempt
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'query_type': 'SELECT',
            'sql': sql,
            'original_prompt': parsed_query.get('original_prompt', '') if parsed_query else '',
            'status': 'pending'
        }
        
        try:
            # Execute the query
            result = self.db.execute(sql)
            
            # Update audit log
            audit_entry['status'] = 'success'
            audit_entry['rows_returned'] = len(result)
            
            # Log successful execution
            self._log_audit_entry(audit_entry)
            
            return {
                'success': True,
                'data': result,
                'sql': sql,
                'rows_returned': len(result),
                'execution_time': audit_entry['timestamp']
            }
            
        except Exception as e:
            # Update audit log with error
            audit_entry['status'] = 'error'
            audit_entry['error'] = str(e)
            
            # Log failed execution
            self._log_audit_entry(audit_entry)
            
            return {
                'success': False,
                'error': str(e),
                'sql': sql,
                'execution_time': audit_entry['timestamp']
            }

    def _log_audit_entry(self, entry: Dict[str, Any]):
        """Log audit entry to database"""
        try:
            # Create audit_logs table if it doesn't exist
            self._ensure_audit_table()
            
            # Insert audit entry
            self.db.insert('audit_logs', {
                'timestamp': entry['timestamp'],
                'query_type': entry['query_type'],
                'sql_query': entry['sql'],
                'original_prompt': entry['original_prompt'],
                'status': entry['status'],
                'rows_affected': entry.get('rows_returned', entry.get('rows_affected', 0)),
                'error_message': entry.get('error', ''),
                'user_id': 1  # TODO: Get from current session
            })
            
        except Exception as e:
            logger.error(f"Failed to log audit entry: {e}")

    def _ensure_audit_table(self):
        """Ensure audit_logs table exists"""
        create_sql = f'''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id {'SERIAL' if self.db.db_type == 'postgresql' else 'INTEGER'} PRIMARY KEY{' AUTOINCREMENT' if self.db.db_type == 'sqlite' else ''},
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                query_type VARCHAR(20) NOT NULL,
                sql_query TEXT NOT NULL,
                original_prompt TEXT,
                status VARCHAR(20) NOT NULL,
                rows_affected INTEGER DEFAULT 0,
                error_message TEXT,
                user_id INTEGER REFERENCES createsonline_users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
        
        try:
            cursor = self.db.connection.cursor()
            cursor.execute(create_sql)
            self.db.connection.commit()
        except Exception as e:
            logger.error(f"Failed to create audit_logs table: {e}")

    def query_from_natural_language(self, prompt: str) -> Dict[str, Any]:
        """Complete workflow: natural language → SQL → execution → results"""
        
        # Parse the natural language prompt
        parsed_query = self.parse_natural_language(prompt)
        
        # Check safety level
        safety_level = parsed_query['safety_level']
        if safety_level == SafetyLevel.BLOCKED:
            return {
                'success': False,
                'error': f"Query type {parsed_query['query_type'].value} is blocked for safety",
                'prompt': prompt
            }
        
        try:
            # Generate SQL
            sql = self.generate_sql(parsed_query)
            
            # Execute safely
            result = self.execute_safe(sql, parsed_query)
            
            # Add parsed query info to result
            result['parsed_query'] = parsed_query
            result['prompt'] = prompt
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'prompt': prompt,
                'parsed_query': parsed_query
            }

    def explain_query(self, prompt: str) -> Dict[str, Any]:
        """Explain what SQL would be generated without executing it"""
        try:
            parsed_query = self.parse_natural_language(prompt)
            sql = self.generate_sql(parsed_query)
            
            return {
                'success': True,
                'prompt': prompt,
                'parsed_query': parsed_query,
                'generated_sql': sql,
                'explanation': self._generate_explanation(parsed_query, sql),
                'safety_level': parsed_query['safety_level'].value
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'prompt': prompt
            }

    def _generate_explanation(self, parsed_query: Dict[str, Any], sql: str) -> str:
        """Generate human-readable explanation of the query"""
        query_type = parsed_query['query_type']
        table = parsed_query['table']
        conditions = parsed_query['conditions']
        limit = parsed_query['limit']
        
        explanation = f"This will {query_type.value.upper()} data from the '{table}' table"
        
        if conditions:
            condition_strs = []
            for condition in conditions:
                condition_strs.append(f"{condition['column']} {condition['operator']} {condition['value']}")
            explanation += f" where {' and '.join(condition_strs)}"
        
        if limit:
            explanation += f", limited to {limit} rows"
        
        explanation += f". Generated SQL: {sql}"
        
        return explanation

    def get_recent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent query history from audit logs"""
        try:
            self._ensure_audit_table()
            
            sql = f"""
                SELECT timestamp, original_prompt, sql_query, status, rows_affected, error_message
                FROM audit_logs 
                ORDER BY timestamp DESC 
                LIMIT {limit}
            """
            
            result = self.db.execute(sql)
            return result
            
        except Exception as e:
            logger.error(f"Failed to get recent queries: {e}")
            return []

# Convenience function for quick access
def create_assistant(db=None):
    """Create a database assistant instance"""
    if db is None:
        # Import the main database module to get DatabaseConnection
        import sys
        import importlib.util
        import os
        
        # Get the path to the main database.py file
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.py')
        
        # Load the database module
        spec = importlib.util.spec_from_file_location("database_main", db_path)
        db_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(db_module)
        
        # Get the database connection
        db = db_module.get_database()
    
    return DatabaseAssistant(db)
