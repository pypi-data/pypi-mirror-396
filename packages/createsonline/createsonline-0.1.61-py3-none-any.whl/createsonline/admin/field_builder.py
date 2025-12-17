# createsonline/admin/field_builder.py
"""
Field Builder - Smart field type selector for adding fields to models
"""

FIELD_TEMPLATES = {
    # Text Fields
    "short_text": {
        "label": "Short Text",
        "description": "For names, titles, usernames (max 255 chars)",
        "sql_type": "String",
        "default_length": 150,
        "examples": "username, title, name, slug, code",
        "icon": ""
    },
    "long_text": {
        "label": "Long Text",
        "description": "For descriptions, bios, comments (unlimited)",
        "sql_type": "Text",
        "default_length": None,
        "examples": "bio, description, content, notes",
        "icon": "📄"
    },
    "email": {
        "label": "Email",
        "description": "Email address with validation",
        "sql_type": "String",
        "default_length": 254,
        "examples": "email, contact_email, support_email",
        "icon": "📧"
    },
    "url": {
        "label": "URL",
        "description": "Website or link URL",
        "sql_type": "String",
        "default_length": 500,
        "examples": "website, profile_url, avatar_url",
        "icon": ""
    },
    "phone": {
        "label": "Phone Number",
        "description": "Phone number with country code",
        "sql_type": "String",
        "default_length": 20,
        "examples": "phone, mobile, contact_number",
        "icon": "📱"
    },
    
    # Number Fields
    "integer": {
        "label": "Integer",
        "description": "Whole numbers (IDs, counts, ages)",
        "sql_type": "Integer",
        "default_length": None,
        "examples": "age, count, quantity, order_number",
        "icon": "🔢"
    },
    "decimal": {
        "label": "Decimal",
        "description": "Numbers with decimals (prices, ratings)",
        "sql_type": "Numeric",
        "default_length": "(10, 2)",
        "examples": "price, rating, salary, discount",
        "icon": "💰"
    },
    "float": {
        "label": "Float",
        "description": "Floating point numbers",
        "sql_type": "Float",
        "default_length": None,
        "examples": "percentage, score, weight",
        "icon": ""
    },
    
    # Boolean & Choice Fields
    "boolean": {
        "label": "Boolean (Yes/No)",
        "description": "True/False checkbox",
        "sql_type": "Boolean",
        "default_length": None,
        "examples": "is_active, is_verified, is_featured",
        "icon": ""
    },
    "choice": {
        "label": "Choice (Enum)",
        "description": "Dropdown selection from predefined options",
        "sql_type": "Enum",
        "default_length": None,
        "examples": "status, role, priority, category",
        "icon": ""
    },
    
    # Date & Time Fields
    "date": {
        "label": "Date",
        "description": "Calendar date (YYYY-MM-DD)",
        "sql_type": "Date",
        "default_length": None,
        "examples": "birth_date, start_date, deadline",
        "icon": "📅"
    },
    "datetime": {
        "label": "Date & Time",
        "description": "Full date with time",
        "sql_type": "DateTime",
        "default_length": None,
        "examples": "created_at, updated_at, published_at",
        "icon": "🕐"
    },
    "time": {
        "label": "Time",
        "description": "Time of day (HH:MM:SS)",
        "sql_type": "Time",
        "default_length": None,
        "examples": "opening_time, closing_time, meeting_time",
        "icon": "⏰"
    },
    
    # File & Media Fields
    "image": {
        "label": "Image",
        "description": "Image file path/URL",
        "sql_type": "String",
        "default_length": 500,
        "examples": "avatar, profile_picture, thumbnail, logo",
        "icon": "🖼"
    },
    "file": {
        "label": "File",
        "description": "Document or file path/URL",
        "sql_type": "String",
        "default_length": 500,
        "examples": "resume, attachment, document, certificate",
        "icon": "📎"
    },
    
    # JSON & Special Fields
    "json": {
        "label": "JSON",
        "description": "Structured data in JSON format",
        "sql_type": "JSON",
        "default_length": None,
        "examples": "settings, metadata, preferences, config",
        "icon": "🗃"
    },
    "uuid": {
        "label": "UUID",
        "description": "Universally unique identifier",
        "sql_type": "String",
        "default_length": 36,
        "examples": "external_id, api_key, token",
        "icon": "🔑"
    },
    
    # Common Use Cases
    "slug": {
        "label": "Slug",
        "description": "URL-friendly identifier (lowercase, hyphens)",
        "sql_type": "String",
        "default_length": 200,
        "examples": "slug, url_slug, permalink",
        "icon": ""
    },
    "color": {
        "label": "Color",
        "description": "Hex color code (#RRGGBB)",
        "sql_type": "String",
        "default_length": 7,
        "examples": "color, theme_color, background_color",
        "icon": ""
    },
    "ip_address": {
        "label": "IP Address",
        "description": "IPv4 or IPv6 address",
        "sql_type": "String",
        "default_length": 45,
        "examples": "ip_address, last_login_ip, created_from_ip",
        "icon": ""
    },
    "password": {
        "label": "Password Hash",
        "description": "Hashed password (DO NOT store plain text!)",
        "sql_type": "String",
        "default_length": 128,
        "examples": "password_hash, api_secret_hash",
        "icon": ""
    },
}


def render_add_field_form(model_name: str) -> str:
    """Render the smart add field form"""
    
    # Group field types by category
    categories = {
        "Text": ["short_text", "long_text", "email", "url", "phone", "slug"],
        "Numbers": ["integer", "decimal", "float"],
        "Date & Time": ["date", "datetime", "time"],
        "Boolean & Choice": ["boolean", "choice"],
        "Files & Media": ["image", "file"],
        "Advanced": ["json", "uuid", "color", "ip_address", "password"],
    }
    
    # Build field type selector HTML
    field_types_html = ""
    for category, field_keys in categories.items():
        field_types_html += f'<optgroup label="{category}">'
        for key in field_keys:
            template = FIELD_TEMPLATES[key]
            field_types_html += f'''
                <option value="{key}" 
                    data-sql-type="{template['sql_type']}" 
                    data-length="{template['default_length'] or ''}"
                    data-examples="{template['examples']}"
                    data-description="{template['description']}">
                    {template['icon']} {template['label']}
                </option>
            '''
        field_types_html += '</optgroup>'
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add Field to {model_name} - CREATESONLINE Admin</title>
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
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        .header {{
            margin-bottom: 40px;
        }}
        
        .logo {{
            margin-bottom: 20px;
        }}
        
        .logo img {{
            height: 40px;
        }}
        
        h1 {{
            font-size: 32px;
            font-weight: 700;
            color: #000;
            margin-bottom: 10px;
        }}
        
        .breadcrumb {{
            color: #666;
            font-size: 14px;
        }}
        
        .breadcrumb a {{
            color: #000;
            text-decoration: none;
        }}
        
        .breadcrumb a:hover {{
            text-decoration: underline;
        }}
        
        .form-card {{
            background: #fff;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 40px;
            margin-bottom: 30px;
        }}
        
        .form-group {{
            margin-bottom: 25px;
        }}
        
        label {{
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #000;
        }}
        
        .required {{
            color: #ff0000;
        }}
        
        input[type="text"],
        select,
        textarea {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 15px;
            font-family: inherit;
            transition: all 0.2s;
        }}
        
        input:focus,
        select:focus,
        textarea:focus {{
            outline: none;
            border-color: #000;
        }}
        
        .help-text {{
            font-size: 13px;
            color: #666;
            margin-top: 6px;
        }}
        
        .field-preview {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
            margin-top: 10px;
            display: none;
        }}
        
        .field-preview.active {{
            display: block;
        }}
        
        .preview-label {{
            font-size: 12px;
            font-weight: 600;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        
        .preview-content {{
            font-size: 14px;
            color: #000;
        }}
        
        .checkbox-group {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}
        
        .checkbox-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        input[type="checkbox"] {{
            width: 20px;
            height: 20px;
            cursor: pointer;
        }}
        
        .btn {{
            padding: 14px 28px;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.2s;
        }}
        
        .btn-primary {{
            background: #000;
            color: #fff;
        }}
        
        .btn-primary:hover {{
            background: #333;
        }}
        
        .btn-secondary {{
            background: #f5f5f5;
            color: #000;
            border: 2px solid #e0e0e0;
        }}
        
        .btn-secondary:hover {{
            background: #e0e0e0;
        }}
        
        .actions {{
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }}
        
        .examples-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }}
        
        .example-chip {{
            padding: 8px 12px;
            background: #f0f0f0;
            border-radius: 6px;
            font-size: 13px;
            text-align: center;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <img src="/logo.png" alt="Logo" onerror="this.style.display='none'">
            </div>
            <h1>Add Field to {model_name}</h1>
            <div class="breadcrumb">
                <a href="/admin">Admin</a> / 
                <a href="/admin/model-manager/{model_name.lower()}">Models</a> / 
                <a href="/admin/model-manager/{model_name.lower()}">{model_name}</a> / 
                Add Field
            </div>
        </div>
        
        <form method="POST" id="addFieldForm">
            <div class="form-card">
                <div class="form-group">
                    <label for="field_type">Field Type <span class="required">*</span></label>
                    <select id="field_type" name="field_type" required>
                        <option value="">Select field type...</option>
                        {field_types_html}
                    </select>
                    <div class="help-text">Choose the type of data this field will store</div>
                    <div class="field-preview" id="fieldPreview">
                        <div class="preview-label">Description</div>
                        <div class="preview-content" id="previewDescription"></div>
                        <div class="preview-label" style="margin-top: 15px;">Common Examples</div>
                        <div class="examples-grid" id="previewExamples"></div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="field_name">Field Name <span class="required">*</span></label>
                    <input type="text" id="field_name" name="field_name" placeholder="e.g., role, phone_number, bio" required>
                    <div class="help-text">Lowercase letters, numbers, and underscores only (e.g., user_role, phone_number)</div>
                </div>
                
                <div class="form-group" id="lengthGroup">
                    <label for="field_length">Max Length</label>
                    <input type="number" id="field_length" name="field_length" placeholder="150">
                    <div class="help-text">Maximum character length (leave empty for unlimited)</div>
                </div>
                
                <div class="form-group">
                    <label for="default_value">Default Value</label>
                    <input type="text" id="default_value" name="default_value" placeholder="Optional default value">
                    <div class="help-text">Value to use when creating new records (optional)</div>
                </div>
                
                <div class="form-group">
                    <label>Constraints</label>
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" id="required" name="required" value="1">
                            <label for="required" style="margin: 0;">Required (NOT NULL)</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="unique" name="unique" value="1">
                            <label for="unique" style="margin: 0;">Unique</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="index" name="index" value="1" checked>
                            <label for="index" style="margin: 0;">Indexed (faster searches)</label>
                        </div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="help_text">Help Text</label>
                    <textarea id="help_text" name="help_text" rows="2" placeholder="Helpful description for users filling out forms"></textarea>
                    <div class="help-text">This will be shown in forms to help users understand what to enter</div>
                </div>
            </div>
            
            <div class="actions">
                <button type="submit" class="btn btn-primary"> Add Field</button>
                <a href="/admin/model-manager/{model_name.lower()}" class="btn btn-secondary">Cancel</a>
            </div>
        </form>
    </div>
    
    <script>
        // Field type selector preview
        const fieldTypeSelect = document.getElementById('field_type');
        const fieldPreview = document.getElementById('fieldPreview');
        const previewDescription = document.getElementById('previewDescription');
        const previewExamples = document.getElementById('previewExamples');
        const lengthGroup = document.getElementById('lengthGroup');
        const fieldLengthInput = document.getElementById('field_length');
        
        fieldTypeSelect.addEventListener('change', function() {{
            const selectedOption = this.options[this.selectedIndex];
            
            if (selectedOption.value) {{
                const description = selectedOption.getAttribute('data-description');
                const examples = selectedOption.getAttribute('data-examples').split(', ');
                const length = selectedOption.getAttribute('data-length');
                
                // Show preview
                fieldPreview.classList.add('active');
                previewDescription.textContent = description;
                
                // Show examples
                previewExamples.innerHTML = examples.map(ex => 
                    `<div class="example-chip">${{ex}}</div>`
                ).join('');
                
                // Update length field
                if (length) {{
                    lengthGroup.style.display = 'block';
                    fieldLengthInput.value = length;
                }} else {{
                    lengthGroup.style.display = 'none';
                    fieldLengthInput.value = '';
                }}
            }} else {{
                fieldPreview.classList.remove('active');
                lengthGroup.style.display = 'block';
            }}
        }});
        
        // Auto-format field name
        const fieldNameInput = document.getElementById('field_name');
        fieldNameInput.addEventListener('input', function() {{
            this.value = this.value
                .toLowerCase()
                .replace(/[^a-z0-9_]/g, '_')
                .replace(/_+/g, '_')
                .replace(/^_|_$/g, '');
        }});
    </script>
</body>
</html>
"""
    return html
