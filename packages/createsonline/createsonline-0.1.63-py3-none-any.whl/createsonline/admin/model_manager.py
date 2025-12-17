# createsonline/admin/model_manager.py
"""
Model Manager - View and edit model structure (fields, relationships)
"""
from typing import Dict, Any
from sqlalchemy import inspect as sql_inspect


class ModelManager:
    """Manage model structure - view/edit fields and relationships"""
    
    def __init__(self, model_class, admin_site):
        self.model_class = model_class
        self.admin_site = admin_site
        self.model_name = model_class.__name__
    
    async def render(self, request) -> str:
        """Render model structure management page"""
        
        # Get model information
        mapper = sql_inspect(self.model_class)
        
        # Get columns (fields)
        fields_html = ""
        for column in mapper.columns:
            field_type = type(column.type).__name__
            field_length = getattr(column.type, 'length', '')
            length_display = f"({field_length})" if field_length else ""
            
            nullable = "NULL" if column.nullable else "NOT NULL"
            primary_key = "PRIMARY KEY" if column.primary_key else ""
            unique = "UNIQUE" if column.unique else ""
            
            badges = ""
            if primary_key:
                badges += '<span class="badge badge-primary">PK</span>'
            if unique and not primary_key:
                badges += '<span class="badge badge-unique">UNIQUE</span>'
            if not column.nullable:
                badges += '<span class="badge badge-required">REQUIRED</span>'
            
            fields_html += f"""
            <tr>
                <td><strong>{column.name}</strong></td>
                <td>{field_type}{length_display}</td>
                <td>{badges}</td>
                <td>
                    <a href="/admin/model-manager/{self.model_name.lower()}/field/{column.name}/edit" class="btn-small">Edit</a>
                    {'' if column.primary_key else '<a href="/admin/model-manager/' + self.model_name.lower() + '/field/' + column.name + '/delete" class="btn-small btn-danger">Delete</a>'}
                </td>
            </tr>
            """
        
        # Get relationships
        relationships_html = ""
        for rel in mapper.relationships:
            rel_type = "One-to-Many" if rel.uselist else "Many-to-One"
            target = rel.mapper.class_.__name__
            
            relationships_html += f"""
            <tr>
                <td><strong>{rel.key}</strong></td>
                <td>{target}</td>
                <td><span class="badge badge-relation">{rel_type}</span></td>
                <td>
                    <a href="/admin/model-manager/{self.model_name.lower()}/relationship/{rel.key}/edit" class="btn-small">Edit</a>
                    <a href="/admin/model-manager/{self.model_name.lower()}/relationship/{rel.key}/delete" class="btn-small btn-danger">Delete</a>
                </td>
            </tr>
            """
        
        if not relationships_html:
            relationships_html = '<tr><td colspan="4" style="text-align: center; padding: 30px; color: #888;">No relationships defined</td></tr>'
        
        # Get record count
        from createsonline.admin.integration import get_database_session
        session = get_database_session()
        record_count = 0
        if session:
            try:
                record_count = session.query(self.model_class).count()
                session.close()
            except:
                pass
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manage {self.model_name} Model - CREATESONLINE Admin</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #ffffff;
            color: #000000;
            padding: 0;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: #000000;
            color: #ffffff;
            padding: 20px 40px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        
        .logo {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .logo img {{
            height: 40px;
        }}
        
        h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .breadcrumb {{
            color: #888;
            font-size: 0.9em;
        }}
        
        .breadcrumb a {{
            color: #fff;
            text-decoration: none;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: 700;
            color: #000;
        }}
        
        .section {{
            background: #ffffff;
            padding: 30px;
            border-radius: 12px;
            border: 2px solid #e0e0e0;
            margin-bottom: 30px;
        }}
        
        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        h2 {{
            font-size: 1.5em;
            color: #000;
        }}
        
        .btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.2s;
        }}
        
        .btn-primary {{
            background: #000000;
            color: #ffffff;
        }}
        
        .btn-primary:hover {{
            background: #333333;
        }}
        
        .btn-secondary {{
            background: #f5f5f5;
            color: #000;
            border: 2px solid #e0e0e0;
        }}
        
        .btn-secondary:hover {{
            background: #e0e0e0;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            text-align: left;
            padding: 12px;
            background: #f5f5f5;
            border-bottom: 2px solid #e0e0e0;
            font-weight: 600;
            color: #000;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        tr:hover {{
            background: #fafafa;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 600;
            margin-right: 5px;
        }}
        
        .badge-primary {{
            background: #000;
            color: #fff;
        }}
        
        .badge-unique {{
            background: #666;
            color: #fff;
        }}
        
        .badge-required {{
            background: #333;
            color: #fff;
        }}
        
        .badge-relation {{
            background: #999;
            color: #fff;
        }}
        
        .btn-small {{
            padding: 6px 12px;
            background: #000;
            color: #fff;
            border: none;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.85em;
            margin-right: 5px;
            display: inline-block;
            transition: all 0.2s;
        }}
        
        .btn-small:hover {{
            background: #333;
        }}
        
        .btn-danger {{
            background: #ff0000;
        }}
        
        .btn-danger:hover {{
            background: #cc0000;
        }}
        
        .actions {{
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <img src="/logo.png" alt="Logo" onerror="this.style.display='none'">
            </div>
            <h1>{self.model_name} Model</h1>
            <div class="breadcrumb">
                <a href="/admin">Admin</a> / 
                <a href="/admin">Models</a> / 
                {self.model_name}
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Records</div>
                <div class="stat-value">{record_count}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Fields</div>
                <div class="stat-value">{len(mapper.columns)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Relationships</div>
                <div class="stat-value">{len(mapper.relationships)}</div>
            </div>
        </div>
        
        <div class="actions">
            <a href="/admin/{self.model_name.lower()}" class="btn btn-primary"> View Records</a>
            <a href="/admin/{self.model_name.lower()}/add" class="btn btn-secondary">+ Add Record</a>
            <a href="/admin" class="btn btn-secondary">← Back to Dashboard</a>
        </div>
        
        <div class="section">
            <div class="section-header">
                <h2>Fields</h2>
                <a href="/admin/model-manager/{self.model_name.lower()}/field/add" class="btn btn-primary">+ Add Field</a>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Field Name</th>
                        <th>Type</th>
                        <th>Constraints</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {fields_html}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <div class="section-header">
                <h2>Relationships</h2>
                <a href="/admin/model-manager/{self.model_name.lower()}/relationship/add" class="btn btn-primary">+ Add Relationship</a>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Relationship Name</th>
                        <th>Target Model</th>
                        <th>Type</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {relationships_html}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""
        return html
