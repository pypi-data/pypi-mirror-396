# createsonline/admin/integration.py
"""
CREATESONLINE Admin Integration

Integrates all admin components: CRUD, permissions, content, dashboard.
This file extends the existing AdminSite with new features.
"""
from typing import Dict, Any, Optional
import os


async def integrate_auto_crud(admin_site, request):
    """
    Integrate auto-CRUD views into admin site
    
    This function adds routes for all registered models:
    - /admin/{model}/          - List view
    - /admin/{model}/add       - Create view
    - /admin/{model}/{id}/edit - Edit view
    - /admin/{model}/{id}/delete - Delete view
    - /admin/create-model      - Model creator
    - /admin/model-manager/{model} - Model structure manager
    """
    from createsonline.admin.crud import ListView, CreateView, EditView, DeleteView
    from createsonline.admin.user_forms import UserCreateForm, UserEditForm
    from createsonline.admin.model_creator import ModelCreator
    from createsonline.admin.model_manager import ModelManager
    from createsonline.auth.models import User
    
    # Get URL path
    path = getattr(request, 'path', '/')
    method = getattr(request, 'method', 'GET')
    
    # Parse URL pattern: /admin/{model}/{id?}/{action?}
    parts = [p for p in path.split('/') if p]
    
    if len(parts) < 2:
        return None
    
    if parts[0] != 'admin':
        return None
    
    # Check if this is the model manager route
    if parts[1] == 'model-manager' and len(parts) >= 3:
        model_name = parts[2]
        
        
        # Find registered model
        model_class = None
        for registered_name, registered_admin in admin_site._registry.items():
            if registered_name.lower() == model_name.lower():
                model_class = registered_admin.model
                break
        
        if model_class:
            # Check if this is add field route
            if len(parts) >= 5 and parts[3] == 'field' and parts[4] == 'add':
                from createsonline.admin.field_builder import render_add_field_form
                html = render_add_field_form(model_class.__name__)
                from createsonline.admin.interface import InternalHTMLResponse
                return InternalHTMLResponse(html)
            
            # Default: show model structure
            manager = ModelManager(model_class, admin_site)
            html = await manager.render(request)
            from createsonline.admin.interface import InternalHTMLResponse
            return InternalHTMLResponse(html)
        else:
            return None
    
    # Check if this is the model creator route
    if parts[1] == 'create-model':
        creator = ModelCreator(admin_site)
        
        if method == 'POST':
            data = await parse_form_data(request)
            success, message = await creator.create_model(data)
            
            if success:
                # Show success page
                from createsonline.admin.interface import InternalHTMLResponse
                success_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Model Created - CREATESONLINE Admin</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #ffffff;
            padding: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }}
        .success-box {{
            background: #1a1a1a;
            border: 1px solid #2a2a2a;
            border-radius: 12px;
            padding: 40px;
            max-width: 600px;
            text-align: center;
        }}
        h1 {{
            color: #4CAF50;
            margin-bottom: 20px;
        }}
        p {{
            color: #aaa;
            margin-bottom: 30px;
        }}
        .btn {{
            padding: 12px 30px;
            background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 100%);
            color: #0a0a0a;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="success-box">
        <h1>âœ“ Success!</h1>
        <p>{message}</p>
        <p>Next steps:<br>
        1. Run <code>createsonline-admin migrate</code> to create the database table<br>
        2. Register the model in your admin.py file<br>
        3. Refresh the admin to see your new model</p>
        <a href="/admin" class="btn">Back to Admin</a>
    </div>
</body>
</html>"""
                return InternalHTMLResponse(success_html)
            else:
                html = await creator.render_form(errors={'model_name': message})
                from createsonline.admin.interface import InternalHTMLResponse
                return InternalHTMLResponse(html)
        else:
            html = await creator.render_form()
            from createsonline.admin.interface import InternalHTMLResponse
            return InternalHTMLResponse(html)
    
    model_name = parts[1]
    
    # Find registered model
    model_admin = None
    model_class = None
    
    for registered_name, registered_admin in admin_site._registry.items():
        if registered_name.lower() == model_name.lower():
            model_admin = registered_admin
            model_class = registered_admin.model
            break
    
    if not model_class:
        return None
    
    # Get database session
    session = get_database_session()
    if not session:
        return None
    
    # Check if this is User model - use custom forms
    is_user_model = model_class == User
    
    # Route to appropriate view
    try:
        if len(parts) == 2:
            # List view
            list_view = ListView(model_class, session, admin_site)
            
            # Get query parameters
            page = int(getattr(request, 'query_params', {}).get('page', 1))
            search = getattr(request, 'query_params', {}).get('search', '')
            
            html = await list_view.render(request, page=page, search=search)
            
            from createsonline.admin.interface import InternalHTMLResponse
            return InternalHTMLResponse(html)
        
        elif len(parts) == 3 and parts[2] == 'add':
            # Create view - use custom form for User model
            if is_user_model:
                create_view = UserCreateForm(session, admin_site)
            else:
                create_view = CreateView(model_class, session, admin_site)
            
            if method == 'POST':
                # Parse form data
                data = await parse_form_data(request)
                success, obj, errors = await create_view.save(request, data)
                
                if success:
                    # Show success message if password was generated
                    if is_user_model and hasattr(obj, '_generated_password'):
                        # For now, redirect with success - could add flash message later
                        pass
                    
                    # Redirect to list view
                    from createsonline.admin.interface import InternalResponse
                    return InternalResponse(
                        b'',
                        status_code=302,
                        headers={'location': f'/admin/{model_name}'}
                    )
                else:
                    html = await create_view.render(request, errors=errors, data=data)
                    from createsonline.admin.interface import InternalHTMLResponse
                    return InternalHTMLResponse(html)
            else:
                html = await create_view.render(request)
                from createsonline.admin.interface import InternalHTMLResponse
                return InternalHTMLResponse(html)
        
        elif len(parts) == 4:
            obj_id = int(parts[2])
            action = parts[3]
            
            if action == 'edit':
                # Edit view - use custom form for User model
                if is_user_model:
                    edit_view = UserEditForm(obj_id, session, admin_site)
                else:
                    edit_view = EditView(model_class, session, admin_site)
                
                if method == 'POST':
                    data = await parse_form_data(request)
                    success, obj, errors = await edit_view.save(request, data)
                    
                    if success:
                        from createsonline.admin.interface import InternalResponse
                        return InternalResponse(
                            b'',
                            status_code=302,
                            headers={'location': f'/admin/{model_name}'}
                        )
                    else:
                        html = await edit_view.render(request, errors=errors)
                        from createsonline.admin.interface import InternalHTMLResponse
                        return InternalHTMLResponse(html)
                else:
                    html = await edit_view.render(request)
                    from createsonline.admin.interface import InternalHTMLResponse
                    return InternalHTMLResponse(html)
            
            elif action == 'delete':
                # Delete view
                delete_view = DeleteView(model_class, session, admin_site)
                
                if method == 'POST':
                    success, message = await delete_view.delete(request, obj_id)
                    
                    from createsonline.admin.interface import InternalResponse
                    return InternalResponse(
                        b'',
                        status_code=302,
                        headers={'location': f'/admin/{model_name}'}
                    )
                else:
                    html = await delete_view.render(request, obj_id)
                    from createsonline.admin.interface import InternalHTMLResponse
                    return InternalHTMLResponse(html)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None
    
    return None


def get_database_session():
    """Get database session"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        database_url = os.getenv("DATABASE_URL", "sqlite:///./createsonline.db")
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(bind=engine)
        
        return SessionLocal()
    except Exception as e:
        return None


async def parse_form_data(request) -> Dict[str, Any]:
    """Parse form data from request"""
    try:
        from urllib.parse import unquote_plus
        
        content_type = getattr(request, 'headers', {}).get('content-type', '')
        
        if 'application/json' in content_type:
            return await request.json()
        else:
            # Parse form-urlencoded
            body = await request.body() if hasattr(request, 'body') else b''
            data = {}
            
            if body:
                body_str = body.decode('utf-8')
                for pair in body_str.split('&'):
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        data[unquote_plus(key)] = unquote_plus(value)
            
            return data
    except Exception as e:
        return {}


async def load_user_from_database(username: str, password: str):
    """
    Load and authenticate user from database
    
    Returns:
        User object if authenticated, None otherwise
    """
    try:
        from createsonline.auth.models import User
        
        session = get_database_session()
        if not session:
            return None
        
        try:
            user = session.query(User).filter_by(username=username).first()
            
            if user and user.is_staff and user.verify_password(password):
                # Record login
                user.record_login_attempt(True)
                session.commit()
                
                return user
            elif user:
                # Record failed attempt
                user.record_login_attempt(False)
                session.commit()
            
            return None
        finally:
            session.close()
    
    except Exception as e:
        return None


async def enhance_dashboard(admin_site, request, user):
    """
    Render enhanced dashboard with insights
    
    Args:
        admin_site: AdminSite instance
        request: Request object
        user: Authenticated user
    
    Returns:
        HTML response with dashboard
    """
    try:
        from createsonline.admin.modern_dashboard import ModernAdminDashboard
        from createsonline.admin.interface import InternalHTMLResponse
        
        dashboard = ModernAdminDashboard(admin_site)
        html = await dashboard.render(request, user)
        
        return InternalHTMLResponse(html)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Fallback to default dashboard
        return await admin_site._show_dashboard(request)


def check_permissions(user, permission: str) -> bool:
    """
    Check if user has permission
    
    Args:
        user: User object
        permission: Permission string like "auth.add_user"
    
    Returns:
        True if user has permission
    """
    if not user:
        return False
    
    if hasattr(user, 'is_superuser') and user.is_superuser:
        return True
    
    if hasattr(user, 'has_permission'):
        return user.has_permission(permission)
    
    return False


async def show_permission_denied(request, message: str = "Permission denied"):
    """Show permission denied page"""
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Permission Denied - CREATESONLINE Admin</title>
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
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 600px;
            background: #1a1a1a;
            padding: 50px;
            border-radius: 12px;
            border: 1px solid #2a2a2a;
            text-align: center;
        }}
        
        .error-icon {{
            font-size: 5em;
            margin-bottom: 20px;
        }}
        
        h1 {{
            font-size: 2.5em;
            background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }}
        
        p {{
            color: #b0b0b0;
            font-size: 1.2em;
            margin-bottom: 30px;
        }}
        
        .btn {{
            padding: 12px 30px;
            background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 100%);
            color: #0a0a0a;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="error-icon">ðŸ”’</div>
        <h1>Permission Denied</h1>
        <p>{message}</p>
        <a href="/admin" class="btn">Go to Dashboard</a>
    </div>
</body>
</html>
"""
    from createsonline.admin.interface import InternalHTMLResponse
    return InternalHTMLResponse(html, status_code=403)
