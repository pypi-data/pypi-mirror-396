# createsonline/admin/user_forms.py
"""
Custom User forms for Add/Edit with password generation and validation
"""
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from createsonline.auth.models import User, hash_password, verify_password
import secrets
import string


class UserCreateForm:
    """Custom form for creating users"""
    
    def __init__(self, session: Session, admin_site):
        self.session = session
        self.admin_site = admin_site
    
    async def render(self, request, errors: Dict = None, data: Dict = None) -> str:
        """Render user creation form"""
        errors = errors or {}
        data = data or {}
        
        return self._generate_form_html(errors, data, is_edit=False)
    
    async def save(self, request, data: Dict) -> Tuple[bool, Any, Dict]:
        """
        Save new user with validation
        
        Returns:
            Tuple of (success, user_object, errors)
        """
        errors = {}
        
        # Validate required fields
        if not data.get('username'):
            errors['username'] = 'Username is required'
        
        if not data.get('email'):
            errors['email'] = 'Email is required'
        
        # Check if username already exists
        if data.get('username'):
            existing_user = self.session.query(User).filter_by(username=data['username']).first()
            if existing_user:
                errors['username'] = f'Username "{data["username"]}" is already taken'
        
        # Check if email already exists
        if data.get('email'):
            existing_email = self.session.query(User).filter_by(email=data['email']).first()
            if existing_email:
                errors['email'] = f'Email "{data["email"]}" is already in use'
        
        # Handle password
        password = None
        if data.get('use_generated_password'):
            # Generate random password
            password = self._generate_password()
            generated_password_display = password  # Store for display
        elif data.get('password') and data.get('password_confirm'):
            # User provided password
            if data['password'] != data['password_confirm']:
                errors['password_confirm'] = 'Passwords do not match'
            else:
                password = data['password']
                generated_password_display = None
        else:
            errors['password'] = 'Please either generate a password or enter one manually'
        
        if errors:
            return False, None, errors
        
        try:
            # Create user
            user = User(
                username=data['username'],
                email=data['email'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                password_hash=hash_password(password),
                is_active=data.get('is_active', False) == 'on',
                is_staff=data.get('is_staff', False) == 'on',
                is_superuser=data.get('is_superuser', False) == 'on'
            )
            
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            
            # Store generated password for display if applicable
            if generated_password_display:
                user._generated_password = generated_password_display
            
            return True, user, {}
            
        except Exception as e:
            self.session.rollback()
            return False, None, {'__all__': f'Error creating user: {str(e)}'}
    
    def _generate_password(self, length: int = 16) -> str:
        """Generate a secure random password"""
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    def _generate_form_html(self, errors: Dict, data: Dict, is_edit: bool = False) -> str:
        """Generate form HTML"""
        
        # Build error messages
        def get_error(field):
            return f'<div class="error-message">{errors.get(field)}</div>' if errors.get(field) else ''
        
        general_error = errors.get('__all__', '')
        general_error_html = f'<div class="error-message general-error">{general_error}</div>' if general_error else ''
        
        # Password section for create form
        password_section = f"""
            <div class="form-section">
                <h3>Password</h3>
                
                <div class="password-options">
                    <label class="radio-option">
                        <input type="radio" name="password_method" value="generate" checked onchange="togglePasswordFields()">
                        Generate secure password automatically
                    </label>
                    
                    <label class="radio-option">
                        <input type="radio" name="password_method" value="manual" onchange="togglePasswordFields()">
                        Enter password manually
                    </label>
                </div>
                
                <div id="manual-password-fields" style="display: none;">
                    <div class="form-group">
                        <label>Password *</label>
                        <input type="password" name="password" id="password" value="">
                        {get_error('password')}
                    </div>
                    
                    <div class="form-group">
                        <label>Confirm Password *</label>
                        <input type="password" name="password_confirm" id="password_confirm" value="">
                        {get_error('password_confirm')}
                    </div>
                </div>
                
                <input type="hidden" name="use_generated_password" id="use_generated_password" value="on">
            </div>
        """ if not is_edit else ""
        
        # Edit password section
        edit_password_section = f"""
            <div class="form-section">
                <h3>Change Password (Optional)</h3>
                
                <div class="form-group">
                    <label>Current Password</label>
                    <input type="password" name="current_password" value="">
                    <div class="help-text">Leave blank to keep current password</div>
                    {get_error('current_password')}
                </div>
                
                <div class="form-group">
                    <label>New Password</label>
                    <input type="password" name="new_password" value="">
                    {get_error('new_password')}
                </div>
                
                <div class="form-group">
                    <label>Confirm New Password</label>
                    <input type="password" name="new_password_confirm" value="">
                    {get_error('new_password_confirm')}
                </div>
            </div>
        """ if is_edit else ""
        
        action_url = "/admin/user/add" if not is_edit else f"/admin/user/{data.get('id', '')}/edit"
        title = "Add User" if not is_edit else f"Edit User: {data.get('username', '')}"
        
        html = f"""<!DOCTYPE html>
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
            background: #fafafa;
            color: #1a1a1a;
            padding: 20px;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        
        .header {{
            background: #000000;
            padding: 20px 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }}
        
        h1 {{
            font-size: 2em;
            color: #ffffff;
        }}
        
        .breadcrumb {{
            margin-top: 15px;
            color: rgba(255, 255, 255, 0.7);
        }}
        
        .breadcrumb a {{
            color: #fff;
            text-decoration: none;
            transition: color 0.2s;
        }}
        
        .breadcrumb a:hover {{
            color: rgba(255, 255, 255, 0.9);
        }}
        
        .form-container {{
            background: #ffffff;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            border: 1px solid #e5e5e5;
        }}
        
        .form-section {{
            margin-bottom: 35px;
            padding-bottom: 35px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .form-section:last-of-type {{
            border-bottom: none;
        }}
        
        h3 {{
            font-size: 1.3em;
            margin-bottom: 20px;
            color: #1a1a1a;
            font-weight: 600;
        }}
        
        .form-group {{
            margin-bottom: 20px;
        }}
        
        label {{
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #666;
        }}
        
        input[type="text"],
        input[type="email"],
        input[type="password"] {{
            width: 100%;
            padding: 12px 15px;
            background: #fafafa;
            border: 2px solid #e5e5e5;
            border-radius: 8px;
            color: #1a1a1a;
            font-size: 1em;
            transition: all 0.2s;
        }}
        
        input[type="text"]:focus,
        input[type="email"]:focus,
        input[type="password"]:focus {{
            outline: none;
            border-color: #000000;
            background: #ffffff;
        }}
        
        .checkbox-group {{
            display: flex;
            gap: 30px;
            margin-top: 15px;
        }}
        
        .checkbox-label {{
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
        }}
        
        input[type="checkbox"] {{
            width: 20px;
            height: 20px;
            cursor: pointer;
            accent-color: #ffffff;
        }}
        
        .password-options {{
            margin-bottom: 20px;
        }}
        
        .radio-option {{
            display: block;
            padding: 15px;
            background: #fafafa;
            border: 2px solid #e5e5e5;
            border-radius: 8px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .radio-option:hover {{
            border-color: #000000;
            background: #ffffff;
        }}
        
        .radio-option input[type="radio"] {{
            margin-right: 10px;
            accent-color: #000000;
        }}
        
        .error-message {{
            color: #dc2626;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .general-error {{
            background: rgba(220, 38, 38, 0.1);
            padding: 15px;
            border-radius: 8px;
            border: 2px solid #dc2626;
            margin-bottom: 20px;
        }}
        
        .help-text {{
            color: #888;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .form-actions {{
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }}
        
        .btn {{
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }}
        
        .btn-primary {{
            background: #000000;
            color: #ffffff;
        }}
        
        .btn-primary:hover {{
            background: #333333;
            transform: translateY(-2px);
        }}
        
        .btn-secondary {{
            background: #e5e5e5;
            color: #1a1a1a;
        }}
        
        .btn-secondary:hover {{
            background: #d0d0d0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="breadcrumb">
                <a href="/admin">Admin</a> / 
                <a href="/admin/user">Users</a> / 
                {title}
            </div>
        </div>
        
        {general_error_html}
        
        <form method="POST" action="{action_url}" class="form-container">
            <div class="form-section">
                <h3>Basic Information</h3>
                
                <div class="form-group">
                    <label>Username *</label>
                    <input type="text" name="username" value="{data.get('username', '')}" required>
                    {get_error('username')}
                    <div class="help-text">Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</div>
                </div>
                
                <div class="form-group">
                    <label>Email *</label>
                    <input type="email" name="email" value="{data.get('email', '')}" required>
                    {get_error('email')}
                </div>
                
                <div class="form-group">
                    <label>First Name</label>
                    <input type="text" name="first_name" value="{data.get('first_name', '')}">
                    {get_error('first_name')}
                </div>
                
                <div class="form-group">
                    <label>Last Name</label>
                    <input type="text" name="last_name" value="{data.get('last_name', '')}">
                    {get_error('last_name')}
                </div>
            </div>
            
            {password_section}
            {edit_password_section}
            
            <div class="form-section">
                <h3>Permissions</h3>
                
                <div class="checkbox-group">
                    <label class="checkbox-label">
                        <input type="checkbox" name="is_active" {"checked" if data.get('is_active', True) else ""}>
                        Is Active
                    </label>
                    
                    <label class="checkbox-label">
                        <input type="checkbox" name="is_staff" {"checked" if data.get('is_staff', False) else ""}>
                        Is Staff
                    </label>
                    
                    <label class="checkbox-label">
                        <input type="checkbox" name="is_superuser" {"checked" if data.get('is_superuser', False) else ""}>
                        Is Superuser
                    </label>
                </div>
                
                <div class="help-text" style="margin-top: 15px;">
                    <strong>Active:</strong> User can login<br>
                    <strong>Staff:</strong> User can access admin<br>
                    <strong>Superuser:</strong> User has all permissions
                </div>
            </div>
            
            <div class="form-actions">
                <button type="submit" class="btn btn-primary">Save User</button>
                <a href="/admin/user" class="btn btn-secondary">Cancel</a>
            </div>
        </form>
    </div>
    
    <script>
        function togglePasswordFields() {{
            const method = document.querySelector('input[name="password_method"]:checked').value;
            const manualFields = document.getElementById('manual-password-fields');
            const useGenerated = document.getElementById('use_generated_password');
            
            if (method === 'generate') {{
                manualFields.style.display = 'none';
                useGenerated.value = 'on';
                document.getElementById('password').value = '';
                document.getElementById('password_confirm').value = '';
            }} else {{
                manualFields.style.display = 'block';
                useGenerated.value = '';
            }}
        }}
    </script>
</body>
</html>
"""
        return html


class UserEditForm:
    """Custom form for editing users"""
    
    def __init__(self, user_id: int, session: Session, admin_site):
        self.user_id = user_id
        self.session = session
        self.admin_site = admin_site
    
    async def render(self, request, errors: Dict = None) -> str:
        """Render user edit form"""
        errors = errors or {}
        
        # Get user
        user = self.session.query(User).filter_by(id=self.user_id).first()
        if not user:
            return "<h1>User not found</h1>"
        
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser
        }
        
        form = UserCreateForm(self.session, self.admin_site)
        return form._generate_form_html(errors, data, is_edit=True)
    
    async def save(self, request, data: Dict) -> Tuple[bool, Any, Dict]:
        """
        Update user with validation
        
        Returns:
            Tuple of (success, user_object, errors)
        """
        errors = {}
        
        # Get user
        user = self.session.query(User).filter_by(id=self.user_id).first()
        if not user:
            return False, None, {'__all__': 'User not found'}
        
        # Validate required fields
        if not data.get('username'):
            errors['username'] = 'Username is required'
        
        if not data.get('email'):
            errors['email'] = 'Email is required'
        
        # Check if username already exists (excluding current user)
        if data.get('username') and data['username'] != user.username:
            existing_user = self.session.query(User).filter_by(username=data['username']).first()
            if existing_user:
                errors['username'] = f'Username "{data["username"]}" is already taken'
        
        # Check if email already exists (excluding current user)
        if data.get('email') and data['email'] != user.email:
            existing_email = self.session.query(User).filter_by(email=data['email']).first()
            if existing_email:
                errors['email'] = f'Email "{data["email"]}" is already in use'
        
        # Handle password change
        if data.get('current_password') or data.get('new_password'):
            if not data.get('current_password'):
                errors['current_password'] = 'Current password is required to change password'
            elif not verify_password(data['current_password'], user.password_hash):
                errors['current_password'] = 'Current password is incorrect'
            elif not data.get('new_password'):
                errors['new_password'] = 'New password is required'
            elif data.get('new_password') != data.get('new_password_confirm'):
                errors['new_password_confirm'] = 'New passwords do not match'
        
        if errors:
            return False, None, errors
        
        try:
            # Update user fields
            user.username = data['username']
            user.email = data['email']
            user.first_name = data.get('first_name', '')
            user.last_name = data.get('last_name', '')
            user.is_active = data.get('is_active') == 'on'
            user.is_staff = data.get('is_staff') == 'on'
            user.is_superuser = data.get('is_superuser') == 'on'
            
            # Update password if changed
            if data.get('new_password') and data.get('current_password'):
                user.password_hash = hash_password(data['new_password'])
            
            self.session.commit()
            self.session.refresh(user)
            
            return True, user, {}
            
        except Exception as e:
            self.session.rollback()
            return False, None, {'__all__': f'Error updating user: {str(e)}'}
