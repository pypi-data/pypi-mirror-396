# createsonline/admin/crud.py
"""
CREATESONLINE Admin Auto-CRUD System

Automatic Create, Read, Update, Delete views for all registered models.
Combines Django Admin's power with Wagtail's beautiful UI.
"""
from typing import Dict, Any, List, Optional, Tuple, Type
from datetime import datetime
import inspect
import re
from sqlalchemy import inspect as sql_inspect
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


class ModelInspector:
    """Inspect SQLAlchemy models to extract field information"""
    
    @staticmethod
    def get_model_fields(model_class) -> List[Dict[str, Any]]:
        """
        Extract field information from SQLAlchemy model
        
        Returns:
            List of field dictionaries with type, label, required, etc.
        """
        fields = []
        mapper = sql_inspect(model_class)
        
        for column in mapper.columns:
            field_info = {
                'name': column.name,
                'label': column.name.replace('_', ' ').title(),
                'type': ModelInspector._get_field_type(column),
                'required': not column.nullable and column.default is None,
                'primary_key': column.primary_key,
                'unique': column.unique,
                'max_length': getattr(column.type, 'length', None),
                'default': column.default,
                'help_text': column.comment or '',
            }
            fields.append(field_info)
        
        return fields
    
    @staticmethod
    def _get_field_type(column) -> str:
        """Determine field type from SQLAlchemy column"""
        from sqlalchemy import Integer, String, Boolean, DateTime, Date, Time, Text, Float, Numeric
        
        column_type = type(column.type).__name__
        
        # Map SQLAlchemy types to HTML input types
        type_mapping = {
            'Integer': 'number',
            'String': 'text',
            'Text': 'textarea',
            'Boolean': 'checkbox',
            'DateTime': 'datetime-local',
            'Date': 'date',
            'Time': 'time',
            'Float': 'number',
            'Numeric': 'number',
        }
        
        # Special cases
        if 'password' in column.name.lower():
            return 'password'
        elif 'email' in column.name.lower():
            return 'email'
        elif 'url' in column.name.lower():
            return 'url'
        elif hasattr(column.type, 'length') and column.type.length and column.type.length > 255:
            return 'textarea'
        
        return type_mapping.get(column_type, 'text')
    
    @staticmethod
    def get_model_name(model_class) -> str:
        """Get model name"""
        return model_class.__name__
    
    @staticmethod
    def get_model_verbose_name(model_class) -> str:
        """Get model verbose name"""
        return model_class.__name__.replace('_', ' ').title()
    
    @staticmethod
    def get_model_verbose_name_plural(model_class) -> str:
        """Get model verbose name plural"""
        name = ModelInspector.get_model_verbose_name(model_class)
        if name.endswith('s'):
            return name + 'es'
        elif name.endswith('y'):
            return name[:-1] + 'ies'
        else:
            return name + 's'


class ListView:
    """List view for models - shows all records in a table"""
    
    def __init__(self, model_class, session: Session, admin_site):
        self.model_class = model_class
        self.session = session
        self.admin_site = admin_site
        self.list_display = []  # Fields to display in list
        self.list_filter = []   # Fields to filter by
        self.search_fields = [] # Fields to search
        self.ordering = []      # Default ordering
        self.list_per_page = 25 # Items per page
    
    async def render(self, request, page: int = 1, search: str = "", filters: Dict = None) -> str:
        """Render list view"""
        filters = filters or {}
        
        # Get model info
        model_name = ModelInspector.get_model_name(self.model_class)
        verbose_name = ModelInspector.get_model_verbose_name(self.model_class)
        verbose_name_plural = ModelInspector.get_model_verbose_name_plural(self.model_class)
        
        # Build query
        query = self.session.query(self.model_class)
        
        # Apply search
        if search and self.search_fields:
            search_conditions = []
            for field in self.search_fields:
                if hasattr(self.model_class, field):
                    col = getattr(self.model_class, field)
                    search_conditions.append(col.like(f'%{search}%'))
            
            if search_conditions:
                from sqlalchemy import or_
                query = query.filter(or_(*search_conditions))
        
        # Apply filters
        for field, value in filters.items():
            if hasattr(self.model_class, field) and value:
                query = query.filter(getattr(self.model_class, field) == value)
        
        # Apply ordering
        if self.ordering:
            for field in self.ordering:
                if field.startswith('-'):
                    query = query.order_by(getattr(self.model_class, field[1:]).desc())
                else:
                    query = query.order_by(getattr(self.model_class, field))
        
        # Get total count
        total_count = query.count()
        
        # Pagination
        offset = (page - 1) * self.list_per_page
        objects = query.limit(self.list_per_page).offset(offset).all()
        
        # Calculate pagination
        total_pages = (total_count + self.list_per_page - 1) // self.list_per_page
        
        # Get fields to display
        all_fields = ModelInspector.get_model_fields(self.model_class)
        
        # Exclude password_hash and other sensitive fields
        excluded_fields = ['password_hash', 'password', 'last_login']
        
        if self.list_display:
            fields = self.list_display
        else:
            fields = [f['name'] for f in all_fields 
                     if not f['primary_key'] 
                     and f['name'] not in excluded_fields][:5]
        
        # Generate HTML
        return self._generate_list_html(
            model_name=model_name,
            verbose_name=verbose_name,
            verbose_name_plural=verbose_name_plural,
            objects=objects,
            fields=fields,
            page=page,
            total_pages=total_pages,
            total_count=total_count,
            search=search,
            filters=filters
        )
    
    def _generate_list_html(self, **kwargs) -> str:
        """Generate beautiful list view HTML"""
        objects = kwargs['objects']
        fields = kwargs['fields']
        model_name = kwargs['model_name']
        verbose_name_plural = kwargs['verbose_name_plural']
        page = kwargs['page']
        total_pages = kwargs['total_pages']
        total_count = kwargs['total_count']
        search = kwargs['search']
        
        # Generate table rows
        rows_html = ""
        for obj in objects:
            cells = ""
            for field in fields:
                value = getattr(obj, field, '')
                if isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d %H:%M')
                elif value is None:
                    value = '-'
                cells += f'<td>{value}</td>'
            
            obj_id = getattr(obj, 'id', '')
            rows_html += f"""
                <tr>
                    {cells}
                    <td class="actions">
                        <a href="/admin/{model_name.lower()}/{obj_id}/edit" class="btn-small">Edit</a>
                        <a href="/admin/{model_name.lower()}/{obj_id}/delete" class="btn-small btn-danger">Delete</a>
                    </td>
                </tr>
            """
        
        # Generate table headers
        headers_html = "".join([f'<th>{field.replace("_", " ").title()}</th>' for field in fields])
        headers_html += '<th>Actions</th>'
        
        # Generate pagination
        pagination_html = ""
        if total_pages > 1:
            pagination_html = '<div class="pagination">'
            if page > 1:
                pagination_html += f'<a href="?page={page-1}" class="btn-small">Previous</a>'
            
            pagination_html += f'<span>Page {page} of {total_pages}</span>'
            
            if page < total_pages:
                pagination_html += f'<a href="?page={page+1}" class="btn-small">Next</a>'
            pagination_html += '</div>'
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{verbose_name_plural} - CREATESONLINE Admin</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #ffffff;
            padding: 20px;
        }}
        
        .header {{
            background: #1a1a1a;
            padding: 20px 30px;
            border-radius: 12px;
            border: 1px solid #2a2a2a;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        h1 {{
            font-size: 2em;
            background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .search-bar {{
            display: flex;
            gap: 10px;
        }}
        
        input[type="search"] {{
            padding: 10px 15px;
            background: #0a0a0a;
            border: 1px solid #3a3a3a;
            border-radius: 8px;
            color: #ffffff;
            width: 300px;
        }}
        
        .btn, .btn-small {{
            padding: 10px 20px;
            background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 100%);
            color: #0a0a0a;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            cursor: pointer;
            font-weight: 600;
            display: inline-block;
        }}
        
        .btn-small {{
            padding: 6px 12px;
            font-size: 0.9em;
        }}
        
        .btn-danger {{
            background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
            color: #ffffff;
        }}
        
        .content {{
            background: #1a1a1a;
            padding: 30px;
            border-radius: 12px;
            border: 1px solid #2a2a2a;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th {{
            text-align: left;
            padding: 12px;
            background: #0a0a0a;
            border-bottom: 2px solid #3a3a3a;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #2a2a2a;
        }}
        
        tr:hover {{
            background: #252525;
        }}
        
        .actions {{
            display: flex;
            gap: 10px;
        }}
        
        .pagination {{
            margin-top: 20px;
            display: flex;
            gap: 15px;
            align-items: center;
            justify-content: center;
        }}
        
        .stats {{
            color: #888;
            margin-bottom: 15px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{verbose_name_plural}</h1>
        <div class="search-bar">
            <input type="search" placeholder="Search..." value="{search}">
            <a href="/admin/{model_name.lower()}/add" class="btn">Add {model_name}</a>
        </div>
    </div>
    
    <div class="content">
        <div class="stats">Showing {total_count} {verbose_name_plural.lower()}</div>
        
        <table>
            <thead>
                <tr>{headers_html}</tr>
            </thead>
            <tbody>
                {rows_html or '<tr><td colspan="100" style="text-align: center; padding: 40px;">No records found</td></tr>'}
            </tbody>
        </table>
        
        {pagination_html}
    </div>
    
    <div style="margin-top: 20px; text-align: center;">
        <a href="/admin" class="btn-small">← Back to Dashboard</a>
    </div>
</body>
</html>
"""
        return html


class CreateView:
    """Create view for models"""
    
    def __init__(self, model_class, session: Session, admin_site):
        self.model_class = model_class
        self.session = session
        self.admin_site = admin_site
    
    async def render(self, request, errors: Dict = None) -> str:
        """Render create form"""
        errors = errors or {}
        fields = ModelInspector.get_model_fields(self.model_class)
        
        # Filter out auto-generated fields
        editable_fields = [f for f in fields if not f['primary_key'] and f['name'] not in ['created_at', 'updated_at', 'date_joined']]
        
        return self._generate_form_html(
            fields=editable_fields,
            errors=errors,
            title=f"Add {ModelInspector.get_model_verbose_name(self.model_class)}",
            action=f"/admin/{ModelInspector.get_model_name(self.model_class).lower()}/add",
            method="POST"
        )
    
    async def save(self, request, data: Dict) -> Tuple[bool, Any, Dict]:
        """
        Save new object
        
        Returns:
            Tuple of (success, object, errors)
        """
        try:
            # Create new instance
            obj = self.model_class(**data)
            self.session.add(obj)
            self.session.commit()
            self.session.refresh(obj)
            return True, obj, {}
        except IntegrityError as e:
            self.session.rollback()
            return False, None, {'__all__': f'Integrity error: {str(e)}'}
        except ValueError as e:
            self.session.rollback()
            return False, None, {'__all__': str(e)}
        except Exception as e:
            self.session.rollback()
            return False, None, {'__all__': f'Error: {str(e)}'}
    
    def _generate_form_html(self, fields, errors, title, action, method, data=None) -> str:
        """Generate beautiful form HTML"""
        data = data or {}
        
        form_fields_html = ""
        for field in fields:
            field_name = field['name']
            field_label = field['label']
            field_type = field['type']
            field_value = data.get(field_name, field.get('default', ''))
            field_required = 'required' if field['required'] else ''
            field_error = errors.get(field_name, '')
            
            error_html = f'<div class="error-message">{field_error}</div>' if field_error else ''
            
            if field_type == 'textarea':
                input_html = f'<textarea name="{field_name}" {field_required}>{field_value}</textarea>'
            elif field_type == 'checkbox':
                checked = 'checked' if field_value else ''
                input_html = f'<input type="checkbox" name="{field_name}" {checked}>'
            else:
                input_html = f'<input type="{field_type}" name="{field_name}" value="{field_value}" {field_required}>'
            
            form_fields_html += f"""
                <div class="form-group">
                    <label>{field_label}{' *' if field['required'] else ''}</label>
                    {input_html}
                    {error_html}
                    {f'<div class="help-text">{field["help_text"]}</div>' if field.get('help_text') else ''}
                </div>
            """
        
        general_error = errors.get('__all__', '')
        general_error_html = f'<div class="error-message general-error">{general_error}</div>' if general_error else ''
        
        model_name = ModelInspector.get_model_name(self.model_class).lower()
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - CREATESONLINE Admin</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #ffffff;
            padding: 20px;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        
        h1 {{
            font-size: 2.5em;
            background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 30px;
        }}
        
        .form-container {{
            background: #1a1a1a;
            padding: 40px;
            border-radius: 12px;
            border: 1px solid #2a2a2a;
        }}
        
        .form-group {{
            margin-bottom: 25px;
        }}
        
        label {{
            display: block;
            margin-bottom: 8px;
            color: #b0b0b0;
            font-weight: 500;
        }}
        
        input, textarea, select {{
            width: 100%;
            padding: 12px 15px;
            background: #0a0a0a;
            border: 1px solid #3a3a3a;
            border-radius: 8px;
            color: #ffffff;
            font-size: 1em;
            font-family: inherit;
        }}
        
        input[type="checkbox"] {{
            width: auto;
        }}
        
        textarea {{
            min-height: 120px;
            resize: vertical;
        }}
        
        input:focus, textarea:focus, select:focus {{
            outline: none;
            border-color: #ffffff;
        }}
        
        .error-message {{
            color: #ff4444;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .general-error {{
            background: #331111;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #ff4444;
            margin-bottom: 20px;
        }}
        
        .help-text {{
            color: #888;
            font-size: 0.85em;
            margin-top: 5px;
        }}
        
        .form-actions {{
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }}
        
        .btn {{
            padding: 12px 30px;
            background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 100%);
            color: #0a0a0a;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            cursor: pointer;
            font-weight: 600;
            font-size: 1em;
        }}
        
        .btn:hover {{
            background: linear-gradient(135deg, #e0e0e0 0%, #c0c0c0 100%);
        }}
        
        .btn-secondary {{
            background: #2a2a2a;
            color: #ffffff;
        }}
        
        .btn-secondary:hover {{
            background: #3a3a3a;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        
        <div class="form-container">
            {general_error_html}
            
            <form method="{method}" action="{action}">
                {form_fields_html}
                
                <div class="form-actions">
                    <button type="submit" class="btn">Save</button>
                    <a href="/admin/{model_name}" class="btn btn-secondary">Cancel</a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
"""
        return html


class EditView(CreateView):
    """Edit view for models - extends CreateView"""
    
    async def render(self, request, obj_id: int, errors: Dict = None) -> str:
        """Render edit form"""
        errors = errors or {}
        obj = self.session.query(self.model_class).get(obj_id)
        
        if not obj:
            return "Object not found"
        
        fields = ModelInspector.get_model_fields(self.model_class)
        editable_fields = [f for f in fields if not f['primary_key'] and f['name'] not in ['created_at', 'updated_at', 'date_joined']]
        
        # Get current values
        data = {f['name']: getattr(obj, f['name'], '') for f in editable_fields}
        
        return self._generate_form_html(
            fields=editable_fields,
            errors=errors,
            title=f"Edit {ModelInspector.get_model_verbose_name(self.model_class)}",
            action=f"/admin/{ModelInspector.get_model_name(self.model_class).lower()}/{obj_id}/edit",
            method="POST",
            data=data
        )
    
    async def save(self, request, obj_id: int, data: Dict) -> Tuple[bool, Any, Dict]:
        """Update object"""
        try:
            obj = self.session.query(self.model_class).get(obj_id)
            if not obj:
                return False, None, {'__all__': 'Object not found'}
            
            # Update fields
            for key, value in data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            
            self.session.commit()
            self.session.refresh(obj)
            return True, obj, {}
        except IntegrityError as e:
            self.session.rollback()
            return False, None, {'__all__': f'Integrity error: {str(e)}'}
        except ValueError as e:
            self.session.rollback()
            return False, None, {'__all__': str(e)}
        except Exception as e:
            self.session.rollback()
            return False, None, {'__all__': f'Error: {str(e)}'}


class DeleteView:
    """Delete view for models"""
    
    def __init__(self, model_class, session: Session, admin_site):
        self.model_class = model_class
        self.session = session
        self.admin_site = admin_site
    
    async def render(self, request, obj_id: int) -> str:
        """Render delete confirmation"""
        obj = self.session.query(self.model_class).get(obj_id)
        
        if not obj:
            return "Object not found"
        
        model_name = ModelInspector.get_model_name(self.model_class)
        verbose_name = ModelInspector.get_model_verbose_name(self.model_class)
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Delete {verbose_name} - CREATESONLINE Admin</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #ffffff;
            padding: 40px 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 600px;
            background: #1a1a1a;
            padding: 40px;
            border-radius: 12px;
            border: 1px solid #2a2a2a;
            text-align: center;
        }}
        
        h1 {{
            font-size: 2em;
            background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }}
        
        p {{
            color: #b0b0b0;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        
        .actions {{
            display: flex;
            gap: 15px;
            justify-content: center;
        }}
        
        .btn {{
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            cursor: pointer;
            font-weight: 600;
            font-size: 1em;
        }}
        
        .btn-danger {{
            background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
            color: #ffffff;
        }}
        
        .btn-secondary {{
            background: #2a2a2a;
            color: #ffffff;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Confirm Deletion</h1>
        <p>Are you sure you want to delete this {verbose_name.lower()}?</p>
        
        <form method="POST" action="/admin/{model_name.lower()}/{obj_id}/delete" class="actions">
            <button type="submit" class="btn btn-danger">Yes, Delete</button>
            <a href="/admin/{model_name.lower()}" class="btn btn-secondary">Cancel</a>
        </form>
    </div>
</body>
</html>
"""
        return html
    
    async def delete(self, request, obj_id: int) -> Tuple[bool, str]:
        """Delete object"""
        try:
            obj = self.session.query(self.model_class).get(obj_id)
            if not obj:
                return False, 'Object not found'
            
            self.session.delete(obj)
            self.session.commit()
            return True, 'Successfully deleted'
        except Exception as e:
            self.session.rollback()
            return False, f'Error deleting object: {str(e)}'
