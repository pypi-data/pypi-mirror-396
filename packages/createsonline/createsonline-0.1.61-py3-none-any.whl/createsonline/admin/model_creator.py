# createsonline/admin/model_creator.py
"""
Model Creator - Create new SQLAlchemy models dynamically
"""
from typing import Dict, List
import os
import re


class ModelCreator:
    """Create new models dynamically"""
    
    def __init__(self, admin_site):
        self.admin_site = admin_site
    
    async def render_form(self, errors: Dict = None) -> str:
        """Render model creation form"""
        errors = errors or {}
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Model - CREATESONLINE Admin</title>
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
            max-width: 900px;
            margin: 0 auto;
        }}
        
        .header {{
            background: #1a1a1a;
            padding: 30px 40px;
            border-radius: 12px;
            border: 1px solid #2a2a2a;
            margin-bottom: 30px;
        }}
        
        h1 {{
            font-size: 2.5em;
            background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .breadcrumb {{
            margin-top: 15px;
            color: #888;
        }}
        
        .breadcrumb a {{
            color: #fff;
            text-decoration: none;
        }}
        
        .form-container {{
            background: #1a1a1a;
            padding: 40px;
            border-radius: 12px;
            border: 1px solid #2a2a2a;
        }}
        
        .form-section {{
            margin-bottom: 35px;
            padding-bottom: 35px;
            border-bottom: 1px solid #2a2a2a;
        }}
        
        h3 {{
            font-size: 1.3em;
            margin-bottom: 20px;
            color: #ccc;
        }}
        
        .form-group {{
            margin-bottom: 20px;
        }}
        
        label {{
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #ccc;
        }}
        
        input[type="text"], select {{
            width: 100%;
            padding: 12px 15px;
            background: #0a0a0a;
            border: 1px solid #3a3a3a;
            border-radius: 6px;
            color: #fff;
            font-size: 1em;
        }}
        
        .help-text {{
            color: #888;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .field-row {{
            background: #0a0a0a;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #3a3a3a;
            margin-bottom: 15px;
        }}
        
        .field-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr 1fr auto;
            gap: 15px;
            align-items: end;
        }}
        
        .btn {{
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 100%);
            color: #0a0a0a;
        }}
        
        .btn-secondary {{
            background: #2a2a2a;
            color: #fff;
        }}
        
        .btn-small {{
            padding: 8px 15px;
            font-size: 0.9em;
        }}
        
        .btn-danger {{
            background: #442222;
            color: #fff;
        }}
        
        .error {{
            color: #ff4444;
            margin-top: 5px;
            font-size: 0.9em;
        }}
        
        .info-box {{
            background: rgba(68, 136, 255, 0.1);
            border: 1px solid #4488ff;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        
        .info-box h4 {{
            color: #4488ff;
            margin-bottom: 10px;
        }}
        
        .info-box ul {{
            margin-left: 20px;
            color: #aaa;
        }}
        
        .form-actions {{
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Create New Model</h1>
            <div class="breadcrumb">
                <a href="/admin">Admin</a> / Create Model
            </div>
        </div>
        
        <div class="info-box">
            <h4> How it works</h4>
            <ul>
                <li>Define your model name and fields</li>
                <li>The system will generate a Python file in your project</li>
                <li>Run migrations to create the database table</li>
                <li>The model will automatically appear in the admin</li>
            </ul>
        </div>
        
        <form method="POST" action="/admin/create-model" class="form-container">
            <div class="form-section">
                <h3>Model Information</h3>
                
                <div class="form-group">
                    <label>Model Name *</label>
                    <input type="text" name="model_name" required placeholder="e.g., Post, Product, Article">
                    <div class="help-text">Use singular form, PascalCase (e.g., BlogPost, UserProfile)</div>
                    {f'<div class="error">{errors.get("model_name", "")}</div>' if errors.get("model_name") else ''}
                </div>
                
                <div class="form-group">
                    <label>Table Name (optional)</label>
                    <input type="text" name="table_name" placeholder="Auto-generated from model name">
                    <div class="help-text">Leave blank to auto-generate (e.g., blog_posts)</div>
                </div>
            </div>
            
            <div class="form-section">
                <h3>Fields</h3>
                
                <div id="fields-container">
                    <!-- Empty by default - user adds fields -->
                </div>
                
                <button type="button" class="btn btn-secondary" onclick="addField()" style="margin-top: 15px;">
                    + Add Field
                </button>
            </div>
            
            <div class="form-section">
                <h3>Relationships (Optional)</h3>
                
                <div id="relationships-container">
                    <!-- Relationships will be added here -->
                </div>
                
                <button type="button" class="btn btn-secondary" onclick="addRelationship()" style="margin-top: 15px;">
                    + Add Relationship
                </button>
                
                <div class="help-text" style="margin-top: 15px;">
                    <strong>Relationship Types:</strong><br>
                    • <strong>One-to-Many:</strong> One User → Many Posts (User has many Posts)<br>
                    • <strong>Many-to-One:</strong> Many Posts → One User (Post belongs to User)<br>
                    • <strong>One-to-One:</strong> One User → One Profile (User has one Profile)<br>
                    • <strong>Many-to-Many:</strong> Many Users ↔ Many Groups (Users have many Groups, Groups have many Users)
                </div>
            </div>
            
            <div class="form-actions">
                <button type="submit" class="btn btn-primary">Create Model</button>
                <a href="/admin" class="btn btn-secondary">Cancel</a>
            </div>
        </form>
    </div>
    
    <script>
        function addField() {{
            const container = document.getElementById('fields-container');
            const fieldRow = document.createElement('div');
            fieldRow.className = 'field-row';
            fieldRow.innerHTML = `
                <div class="field-grid">
                    <div>
                        <label>Field Name</label>
                        <input type="text" name="field_name[]" placeholder="e.g., title, price, status" required>
                    </div>
                    <div>
                        <label>Type</label>
                        <select name="field_type[]">
                            <option value="string" selected>String</option>
                            <option value="text">Text</option>
                            <option value="integer">Integer</option>
                            <option value="boolean">Boolean</option>
                            <option value="datetime">DateTime</option>
                            <option value="float">Float</option>
                        </select>
                    </div>
                    <div>
                        <label>Max Length</label>
                        <input type="text" name="field_length[]" placeholder="e.g., 200">
                    </div>
                    <div>
                        <button type="button" class="btn btn-danger btn-small" onclick="removeField(this)">×</button>
                    </div>
                </div>
            `;
            container.appendChild(fieldRow);
        }}
        
        function removeField(btn) {{
            btn.closest('.field-row').remove();
        }}
        
        function addRelationship() {{
            const container = document.getElementById('relationships-container');
            const relRow = document.createElement('div');
            relRow.className = 'field-row';
            relRow.innerHTML = `
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr auto; gap: 15px; align-items: end;">
                    <div>
                        <label>Related Model</label>
                        <input type="text" name="rel_model[]" placeholder="e.g., User, Category" required>
                    </div>
                    <div>
                        <label>Relationship Type</label>
                        <select name="rel_type[]">
                            <option value="many_to_one">Many-to-One (belongs to)</option>
                            <option value="one_to_many">One-to-Many (has many)</option>
                            <option value="one_to_one">One-to-One</option>
                            <option value="many_to_many">Many-to-Many</option>
                        </select>
                    </div>
                    <div>
                        <label>Field Name</label>
                        <input type="text" name="rel_field[]" placeholder="e.g., author, category" required>
                    </div>
                    <div>
                        <button type="button" class="btn btn-danger btn-small" onclick="removeField(this)">×</button>
                    </div>
                </div>
            `;
            container.appendChild(relRow);
        }}
    </script>
</body>
</html>
"""
    
    async def create_model(self, data: Dict) -> tuple:
        """
        Create a new model file
        
        Returns:
            (success, message)
        """
        try:
            model_name = data.get('model_name', '').strip()
            table_name = data.get('table_name', '').strip()
            
            # Validate model name
            if not model_name:
                return False, "Model name is required"
            
            if not re.match(r'^[A-Z][a-zA-Z0-9]*$', model_name):
                return False, "Model name must be PascalCase (e.g., BlogPost, UserProfile)"
            
            # Auto-generate table name if not provided
            if not table_name:
                # Convert PascalCase to snake_case
                table_name = re.sub(r'(?<!^)(?=[A-Z])', '_', model_name).lower()
                if not table_name.endswith('s'):
                    table_name += 's'
            
            # Get fields
            field_names = data.getlist('field_name[]') if hasattr(data, 'getlist') else data.get('field_name', [])
            field_types = data.getlist('field_type[]') if hasattr(data, 'getlist') else data.get('field_type', [])
            field_lengths = data.getlist('field_length[]') if hasattr(data, 'getlist') else data.get('field_length', [])
            
            # Get relationships
            rel_models = data.getlist('rel_model[]') if hasattr(data, 'getlist') else data.get('rel_model', [])
            rel_types = data.getlist('rel_type[]') if hasattr(data, 'getlist') else data.get('rel_type', [])
            rel_fields = data.getlist('rel_field[]') if hasattr(data, 'getlist') else data.get('rel_field', [])
            
            # Generate model code
            model_code = self._generate_model_code(
                model_name=model_name,
                table_name=table_name,
                fields=list(zip(field_names, field_types, field_lengths)),
                relationships=list(zip(rel_models, rel_types, rel_fields)) if rel_models else []
            )
            
            # Save to file
            models_dir = os.path.join(os.getcwd(), 'models')
            os.makedirs(models_dir, exist_ok=True)
            
            file_path = os.path.join(models_dir, f'{model_name.lower()}.py')
            
            with open(file_path, 'w') as f:
                f.write(model_code)
            
            return True, f"Model '{model_name}' created successfully at {file_path}. Run migrations to create the database table."
            
        except Exception as e:
            return False, f"Error creating model: {str(e)}"
    
    def _generate_model_code(self, model_name: str, table_name: str, fields: List, relationships: List = None) -> str:
        """Generate Python model code with relationships"""
        relationships = relationships or []
        
        # Build field definitions
        field_defs = []
        for field_name, field_type, field_length in fields:
            if not field_name:
                continue
            
            field_def = f"    {field_name} = Column("
            
            if field_type == 'string':
                length = field_length or '200'
                field_def += f"String({length})"
            elif field_type == 'text':
                field_def += "Text"
            elif field_type == 'integer':
                field_def += "Integer"
            elif field_type == 'boolean':
                field_def += "Boolean, default=False"
            elif field_type == 'datetime':
                field_def += "DateTime"
            elif field_type == 'float':
                field_def += "Float"
            
            field_def += ")"
            field_defs.append(field_def)
        
        # Build relationships
        relationship_imports = []
        relationship_defs = []
        foreign_key_defs = []
        
        for rel_model, rel_type, rel_field in relationships:
            if not rel_model or not rel_field:
                continue
            
            # Add ForeignKey import
            if 'ForeignKey' not in relationship_imports:
                relationship_imports.append('ForeignKey')
            
            # Add relationship import
            if 'relationship' not in relationship_imports:
                relationship_imports.append('relationship')
            
            if rel_type == 'many_to_one':
                # Many-to-One: This model belongs to another (e.g., Post belongs to User)
                fk_field = f"{rel_field}_id"
                foreign_key_defs.append(
                    f"    {fk_field} = Column(Integer, ForeignKey('{rel_model.lower()}s.id'))"
                )
                relationship_defs.append(
                    f"    {rel_field} = relationship('{rel_model}', back_populates='{table_name}')"
                )
            
            elif rel_type == 'one_to_many':
                # One-to-Many: This model has many of another (e.g., User has many Posts)
                relationship_defs.append(
                    f"    {rel_field} = relationship('{rel_model}', back_populates='{model_name.lower()}')"
                )
            
            elif rel_type == 'one_to_one':
                # One-to-One: This model has exactly one of another
                fk_field = f"{rel_field}_id"
                foreign_key_defs.append(
                    f"    {fk_field} = Column(Integer, ForeignKey('{rel_model.lower()}s.id'), unique=True)"
                )
                relationship_defs.append(
                    f"    {rel_field} = relationship('{rel_model}', back_populates='{model_name.lower()}', uselist=False)"
                )
            
            elif rel_type == 'many_to_many':
                # Many-to-Many: Requires association table
                association_table = f"{model_name.lower()}_{rel_model.lower()}_association"
                relationship_defs.append(
                    f"    # Many-to-Many: Create association table '{association_table}' manually"
                )
                relationship_defs.append(
                    f"    {rel_field} = relationship('{rel_model}', secondary='{association_table}', back_populates='{table_name}')"
                )
        
        # Combine all field definitions
        all_fields = field_defs + foreign_key_defs
        fields_code = "\n".join(all_fields) if all_fields else "    pass"
        
        # Combine relationships
        relationships_code = "\n".join(relationship_defs) if relationship_defs else ""
        
        # Build imports
        imports = "from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float"
        if relationship_imports:
            imports += ", " + ", ".join(relationship_imports)
        
        code = f'''"""
{model_name} Model
Auto-generated by CREATESONLINE Admin
"""
{imports}
from createsonline.auth.models import AuthBase


class {model_name}(AuthBase):
    """
    {model_name} model
    """
    __tablename__ = '{table_name}'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
{fields_code}
{relationships_code}
    
    def __repr__(self):
        return f"<{model_name} {{self.id}}>"
'''
        
        return code
