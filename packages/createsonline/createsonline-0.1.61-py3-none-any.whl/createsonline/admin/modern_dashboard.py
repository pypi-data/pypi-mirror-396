# createsonline/admin/modern_dashboard.py
"""
CREATESONLINE Modern Admin Dashboard

Clean, database-driven admin interface - NO hardcoded demo data.
Similar to Django Admin and Wagtail Admin.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime


class ModernAdminDashboard:
    """Modern admin dashboard with database-driven content"""
    
    def __init__(self, admin_site):
        self.admin_site = admin_site
    
    async def render(self, request, user=None) -> str:
        """Render the complete admin dashboard"""
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            from createsonline.auth.models import User, Group, Permission
            import os
            
            database_url = os.getenv("DATABASE_URL", "sqlite:///./createsonline.db")
            engine = create_engine(database_url, echo=False)
            SessionLocal = sessionmaker(bind=engine)
            session = SessionLocal()
            
            try:
                # Get users count
                users_count = session.query(User).count()
                users_list = session.query(User).order_by(User.date_joined.desc()).limit(5).all()
                
                # Get groups count
                groups_count = session.query(Group).count()
                
                # Get permissions count
                permissions_count = session.query(Permission).count()
                
                # Get model stats
                model_stats = []
                for model_name, model_admin in self.admin_site._registry.items():
                    model_class = model_admin.model
                    
                    try:
                        count = session.query(model_class).count()
                    except:
                        count = 0
                    
                    model_stats.append({
                        'name': model_name,
                        'verbose_name': model_class.__name__.replace('_', ' ').title(),
                        'count': count,
                        'url': f'/admin/{model_name.lower()}'
                    })
                
                # Render dashboard
                html = self._render_html(
                    users_count=users_count,
                    users_list=users_list,
                    groups_count=groups_count,
                    permissions_count=permissions_count,
                    model_stats=model_stats,
                    user=user
                )
                
                return html
                
            finally:
                session.close()
                
        except Exception as e:
            print(f"Error rendering dashboard: {e}")
            import traceback
            traceback.print_exc()
            return self._render_error()
    
    def _render_html(self, users_count, users_list, groups_count, permissions_count, model_stats, user) -> str:
        """Render dashboard HTML"""
        
        # Users list HTML
        users_html = ""
        if users_list:
            for u in users_list:
                role = "Superuser" if u.is_superuser else ("Staff" if u.is_staff else "User")
                users_html += f"""
                <div class="item">
                    <div class="item-icon">👤</div>
                    <div class="item-info">
                        <div class="item-name">{u.username}</div>
                        <div class="item-meta">{u.email} • {role}</div>
                    </div>
                    <a href="/admin/user/{u.id}/edit" class="item-action">Edit</a>
                </div>
                """
        else:
            users_html = '<div class="empty-state">No users yet</div>'
        
        # Models list HTML
        models_html = ""
        for stat in model_stats:
            models_html += f"""
            <div class="model-card" onclick="window.location.href='{stat['url']}'">
                <div class="model-header">
                    <span class="model-icon"></span>
                    <span class="model-count">{stat['count']}</span>
                </div>
                <div class="model-name">{stat['verbose_name']}</div>
                <div class="model-actions">
                    <a href="{stat['url']}" class="model-link">View all →</a>
                </div>
            </div>
            """
        
        username = user.username if user and hasattr(user, 'username') else 'Admin'
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - CREATESONLINE</title>
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
            padding: 25px 30px;
            border-radius: 12px;
            border: 1px solid #2a2a2a;
            margin-bottom: 30px;
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
        
        .user-info {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        
        .username {{
            color: #b0b0b0;
        }}
        
        .btn-logout {{
            padding: 10px 20px;
            background: #2a2a2a;
            color: #ffffff;
            border: 1px solid #3a3a3a;
            border-radius: 8px;
            text-decoration: none;
            cursor: pointer;
            font-weight: 500;
        }}
        
        .btn-logout:hover {{
            background: #3a3a3a;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .section {{
            background: #1a1a1a;
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #2a2a2a;
        }}
        
        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #2a2a2a;
        }}
        
        .section-title {{
            font-size: 1.3em;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .section-count {{
            color: #888;
            font-size: 0.9em;
        }}
        
        .btn-add {{
            padding: 8px 16px;
            background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 100%);
            color: #0a0a0a;
            border: none;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9em;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        
        .btn-add:hover {{
            background: linear-gradient(135deg, #e0e0e0 0%, #c0c0c0 100%);
        }}
        
        .item {{
            padding: 15px;
            background: #0a0a0a;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .item-icon {{
            font-size: 1.8em;
        }}
        
        .item-info {{
            flex: 1;
        }}
        
        .item-name {{
            font-weight: 600;
            margin-bottom: 4px;
        }}
        
        .item-meta {{
            color: #888;
            font-size: 0.85em;
        }}
        
        .item-action {{
            padding: 6px 12px;
            background: #2a2a2a;
            color: #ffffff;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.85em;
        }}
        
        .item-action:hover {{
            background: #3a3a3a;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 40px;
            color: #666;
        }}
        
        .models-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .model-card {{
            background: #0a0a0a;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #2a2a2a;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .model-card:hover {{
            border-color: #ffffff;
            transform: translateY(-2px);
        }}
        
        .model-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        
        .model-icon {{
            font-size: 2em;
        }}
        
        .model-count {{
            font-size: 1.5em;
            font-weight: 700;
            color: #ffffff;
        }}
        
        .model-name {{
            font-weight: 600;
            margin-bottom: 8px;
        }}
        
        .model-actions {{
            display: flex;
            gap: 10px;
        }}
        
        .model-link {{
            color: #888;
            text-decoration: none;
            font-size: 0.85em;
        }}
        
        .model-link:hover {{
            color: #ffffff;
        }}
        
        .stats-row {{
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .stat-box {{
            flex: 1;
            background: #0a0a0a;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #888;
            font-size: 0.85em;
        }}
        
        @media (max-width: 768px) {{
            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
            
            .models-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>CREATESONLINE Admin</h1>
        <div class="user-info">
            <span class="username">👤 {username}</span>
            <form method="POST" action="/admin/logout" style="display: inline;">
                <button type="submit" class="btn-logout">Logout</button>
            </form>
        </div>
    </div>
    
    <div class="dashboard-grid">
        <!-- Users Section -->
        <div class="section">
            <div class="section-header">
                <div>
                    <div class="section-title">
                        👥 Users
                        <span class="section-count">({users_count})</span>
                    </div>
                </div>
                <a href="/admin/user/add" class="btn-add">
                    <span>+</span> Create User
                </a>
            </div>
            
            <div class="stats-row">
                <div class="stat-box">
                    <div class="stat-value">{users_count}</div>
                    <div class="stat-label">Total Users</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{groups_count}</div>
                    <div class="stat-label">Groups</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{permissions_count}</div>
                    <div class="stat-label">Permissions</div>
                </div>
            </div>
            
            <div class="users-list">
                {users_html}
            </div>
            
            {f'<a href="/admin/user" style="display: block; text-align: center; margin-top: 15px; color: #888; text-decoration: none;">View all users →</a>' if users_count > 5 else ''}
        </div>
        
        <!-- Models Section -->
        <div class="section">
            <div class="section-header">
                <div class="section-title">
                     Models
                    <span class="section-count">({len(model_stats)})</span>
                </div>
            </div>
            
            <div class="models-grid">
                {models_html}
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _render_error(self) -> str:
        """Render error page"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Error - CREATESONLINE Admin</title>
    <style>
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
        .error {{
            text-align: center;
        }}
        h1 {{
            font-size: 3em;
            margin-bottom: 20px;
        }}
        p {{
            color: #888;
            margin-bottom: 30px;
        }}
        a {{
            padding: 12px 24px;
            background: #ffffff;
            color: #0a0a0a;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="error">
        <h1></h1>
        <h2>Database Error</h2>
        <p>Could not connect to database. Please run migrations:</p>
        <code>python -m createsonline.cli.manage migrate</code>
        <br><br>
        <a href="/">Go to Homepage</a>
    </div>
</body>
</html>
"""
