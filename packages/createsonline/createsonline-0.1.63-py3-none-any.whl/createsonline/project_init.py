# createsonline/project_init.py
"""
Automatic Project Initialization

This module automatically creates the project structure when a user
runs their application for the first time. It protects existing files
and only creates missing ones.
"""

import os
from pathlib import Path
import shutil


class ProjectInitializer:
    """Automatically initialize project structure without overwriting user files"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.framework_dir = Path(__file__).parent
        self.user_files_created = []
        self.user_files_skipped = []
        self.verbose = False  # Control print statements
    
    def initialize(self, force: bool = False, verbose: bool = False) -> dict:
        """
        Initialize project structure automatically.
        
        Args:
            force: If True, overwrites existing files (dangerous!)
            verbose: If True, print progress messages
        
        Returns:
            dict with status of created/skipped files
        """
        self.verbose = verbose
        if verbose:
            print(f"\nInitializing CREATESONLINE project structure...")
            print(f"Project root: {self.project_root}")
        
        # Create directories
        self._create_directories()
        
        # ONE-TIME CLEANUP: Remove old v0.1.1 main.py (v0.1.28 only)
        self._cleanup_legacy_main_py()
        
        # Create/update user files (ONLY if they don't exist)
        self._ensure_main_py()
        self._ensure_routes_py()
        self._ensure_user_config_py()
        self._ensure_templates()
        self._ensure_static_files()
        self._ensure_documentation()
        
        # Summary (only if verbose)
        if verbose:
            print(f"\nInitialization complete!")
            if self.user_files_created:
                print(f"Created {len(self.user_files_created)} new files:")
                for f in self.user_files_created:
                    print(f"   * {f}")
            if self.user_files_skipped:
                print(f"Skipped {len(self.user_files_skipped)} existing files (protected):")
                for f in self.user_files_skipped:
                    print(f"   - {f}")
                print(f"   ⊗ {f}")
        
        return {
            "created": self.user_files_created,
            "skipped": self.user_files_skipped,
            "success": True
        }
    
    def _create_directories(self):
        """Create necessary directories"""
        dirs = [
            self.project_root / "templates",
            self.project_root / "static",
            self.project_root / "static" / "css",
            self.project_root / "static" / "js",
            self.project_root / "static" / "images",
        ]
        
        for directory in dirs:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                if self.verbose:
                    print(f"   Created directory: {directory.relative_to(self.project_root)}")
    
    def _create_file(self, filepath: Path, content: str, description: str = None):
        """Create a file only if it doesn't exist"""
        rel_path = filepath.relative_to(self.project_root)
        
        if filepath.exists():
            self.user_files_skipped.append(str(rel_path))
            return False
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content, encoding='utf-8')
        self.user_files_created.append(str(rel_path))
        if description and self.verbose:
            print(f"   {description}: {rel_path}")
        return True
    
    def _cleanup_legacy_main_py(self):
        """
        ONE-TIME CLEANUP (v0.1.28): Remove old v0.1.1 main.py with embedded HTML
        This only runs once to migrate legacy projects to the new template system.
        """
        # Skip legacy backup creation unless explicitly enabled
        if os.getenv("CREATESONLINE_DISABLE_LEGACY_BACKUP", "1").lower() in ("1", "true", "yes"):
            if self.verbose:
                print("   Skipping legacy main.py backup creation (disabled).")
            return

        main_py = self.project_root / "main.py"
        
        if not main_py.exists():
            return
        
        try:
            content = main_py.read_text(encoding='utf-8')
            
            # Check if this is the old v0.1.1 template with embedded HTML
            if 'Template Version: 0.1.1' in content and '@app.get("/")' in content:
                # Backup the old file
                backup_path = self.project_root / "main.py.v0.1.1.backup"
                shutil.copy2(main_py, backup_path)
                
                # Remove the old main.py so new one gets created
                main_py.unlink()
                
                if self.verbose:
                    print(f"     Removed legacy main.py (v0.1.1) - backup saved as main.py.v0.1.1.backup")
                    print(f"    Will create new clean main.py with template support")
                
                self.user_files_created.append("main.py.v0.1.1.backup (backup)")
        except Exception as e:
            # If cleanup fails, just continue - don't break initialization
            if self.verbose:
                print(f"   Warning: Could not cleanup legacy main.py: {e}")
    
    def _ensure_main_py(self):
        """Create main.py if it doesn't exist"""
        main_py = self.project_root / "main.py"
        
        content = '''#!/usr/bin/env python3
"""
CREATESONLINE Application Bootstrap

  UPGRADE-SAFE FILE - Your changes persist across framework updates! 

This file is automatically generated but safe to customize.
"""
from createsonline import create_app
from createsonline.project_init import auto_discover_routes

# Create application
app = create_app(
    title="My CREATESONLINE App",
    description="AI-Native Web Application",
    version="1.0.0",
    debug=True
)

# Auto-discover and register routes (silent)
auto_discover_routes(app)

if __name__ == "__main__":
    from createsonline.server import run_server
    
    # Load environment variables if available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    import os
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    run_server(app, host=host, port=port)
'''
        
        self._create_file(main_py, content, "Created main.py")
    
    def _ensure_routes_py(self):
        """Create routes.py if it doesn't exist"""
        routes_py = self.project_root / "routes.py"
        
        content = '''# routes.py
"""
URL Configuration - YOUR CUSTOM ROUTES

  UPGRADE-SAFE FILE - Your changes persist across framework updates! 

Define your custom URL patterns here.
"""

from createsonline.routing import path
from createsonline import render_template

# ============================================================================
# YOUR CUSTOM VIEW HANDLERS
# ============================================================================

async def home(request):
    """Modern homepage - uses templates/index.html"""
    html = render_template("index.html")
    
    from createsonline.server import InternalHTMLResponse
    return InternalHTMLResponse(html)


async def admin_login(request):
    """Admin login page - uses templates/admin_login.html"""
    html = render_template("admin_login.html")
    
    from createsonline.server import InternalHTMLResponse
    return InternalHTMLResponse(html)


async def about(request):
    """About page"""
    return {"page": "about", "content": "About our application"}


async def not_found(request):
    """Custom 404 error page - uses templates/404.html"""
    html = render_template("404.html")
    
    from createsonline.server import InternalHTMLResponse
    return InternalHTMLResponse(html, status_code=404)


# ============================================================================
# URL PATTERNS - Add your routes here!
# ============================================================================

urlpatterns = [
    path('/', home, name='home'),
    path('/admin', admin_login, name='admin-login'),
    path('/about', about, name='about'),
]

# Add more routes below:
# path('/api/data', get_data, name='api-data'),
# path('/contact', contact_form, methods=['POST'], name='contact'),
'''
        
        self._create_file(routes_py, content, "Created routes.py")
    
    def _ensure_user_config_py(self):
        """Create user_config.py if it doesn't exist"""
        config_py = self.project_root / "user_config.py"
        
        content = '''# user_config.py
"""
User Configuration for CREATESONLINE

  UPGRADE-SAFE FILE - Your changes persist across framework updates! 

Add your custom settings here.
"""

# Application settings
DEBUG = True
SECRET_KEY = "change-this-in-production"

# Database settings (if needed)
# DATABASE_URL = "sqlite:///app.db"
# DATABASE_TIMEOUT = 30

# Custom middleware (optional)
# MIDDLEWARE = [
#     'myapp.middleware.CustomMiddleware',
# ]

# API Keys (use environment variables in production!)
# API_KEY = "your-api-key"

# Add any custom settings you need below:
'''
        
        self._create_file(config_py, content, "Created user_config.py")
    
    def _ensure_templates(self):
        """Copy modern templates from framework if they don't exist"""
        # Try to copy from framework's templates directory first
        framework_templates = self.framework_dir / "templates"
        
        template_files = ["base.html", "index.html", "admin_login.html", "404.html", "500.html"]
        
        for template_name in template_files:
            source = framework_templates / template_name
            dest = self.project_root / "templates" / template_name
            
            # Skip if template already exists
            if dest.exists():
                self.user_files_skipped.append(f"templates/{template_name}")
                continue
            
            # Copy from framework or use fallback
            if source.exists():
                shutil.copy2(source, dest)
                self.user_files_created.append(f"templates/{template_name}")
                if self.verbose:
                    print(f"   Created template: templates/{template_name}")
            else:
                # Fallback to hardcoded templates
                content = self._get_fallback_template(template_name)
                if content:
                    self._create_file(dest, content, f"Created template")
    
    def _ensure_static_files(self):
        """Copy default static files if they don't exist"""
        # Copy from framework's static directory if needed
        framework_static = self.framework_dir / "static"
        project_static = self.project_root / "static"
        
        # Copy CSS files from framework
        css_files = ["test_styles.css"]  # Basic CSS file
        for css_file in css_files:
            source = framework_static / css_file
            dest = project_static / "css" / css_file.replace("test_styles", "style")
            if source.exists() and not dest.exists():
                shutil.copy2(source, dest)
                self.user_files_created.append(f"static/css/{css_file.replace('test_styles', 'style')}")
                if self.verbose:
                    print(f"   Created CSS: static/css/{css_file.replace('test_styles', 'style')}")
        
        # Copy JS files from framework
        js_files = ["test_script.js"]  # Basic JS file
        for js_file in js_files:
            source = framework_static / js_file
            dest = project_static / "js" / js_file.replace("test_script", "app")
            if source.exists() and not dest.exists():
                shutil.copy2(source, dest)
                self.user_files_created.append(f"static/js/{js_file.replace('test_script', 'app')}")
                if self.verbose:
                    print(f"   Created JS: static/js/{js_file.replace('test_script', 'app')}")
        
        # Create favicon files
        self._create_favicon_files()
        
        # Create logo image
        self._create_logo_file()
        
        # Create site.webmanifest
        self._create_webmanifest()
        
        # Create guide.html and examples.html
        self._create_file(
            project_static / "guide.html",
            self._get_guide_html(),
            "Created guide page"
        )
        self._create_file(
            project_static / "examples.html",
            self._get_examples_html(),
            "Created examples page"
        )
    
    def _ensure_documentation(self):
        """Create documentation files"""
        self._create_file(
            self.project_root / "README.md",
            self._get_readme_content(),
            "Created README.md"
        )
    
    def _create_favicon_files(self):
        """Generate default favicon files (SVG and ICO)"""
        # Create favicon.svg (modern browsers)
        svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" fill="#000000"/>
  <text x="50" y="70" font-family="Arial, sans-serif" font-size="70" font-weight="bold" text-anchor="middle" fill="#ffffff">C</text>
</svg>'''
        self._create_file(
            self.project_root / "favicon.svg",
            svg_content,
            "Created favicon.svg"
        )
        
        # Create basic favicon.ico (16x16 transparent PNG in ICO format)
        # Using minimal valid ICO file structure
        import base64
        # This is a valid 16x16 transparent favicon.ico
        ico_base64 = "AAABAAEAEBAAAAAAAABoBQAAFgAAACgAAAAQAAAAIAAAAAEACAAAAAAAAAEAAAAAAAAAAAAAAAEAAAAAAAAAAAAA////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEA"
        
        try:
            ico_bytes = base64.b64decode(ico_base64)
            ico_path = self.project_root / "favicon.ico"
            if not ico_path.exists():
                ico_path.write_bytes(ico_bytes)
                self.user_files_created.append("favicon.ico")
                if self.verbose:
                    print(f"   Created favicon.ico")
        except Exception as e:
            if self.verbose:
                print(f"   Skipped favicon.ico (creation failed: {e})")
    
    def _create_logo_file(self):
        """Generate default logo SVG"""
        logo_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 100">
  <rect width="400" height="100" fill="transparent"/>
  <text x="10" y="70" font-family="Arial, sans-serif" font-size="60" font-weight="bold" fill="#000000">CREATESONLINE</text>
</svg>'''
        self._create_file(
            self.project_root / "logo.png",
            logo_content,
            "Created logo.svg"
        )
        
        # Also create logo.png as SVG (browsers will handle it)
        self._create_file(
            self.project_root / "logo-header-h200@2x.png",
            logo_content,
            "Created logo-header"
        )
    
    def _create_webmanifest(self):
        """Create site.webmanifest for PWA support"""
        manifest_content = '''{
    "name": "CREATESONLINE App",
    "short_name": "CREATESONLINE",
    "icons": [
        {
            "src": "/favicon.svg",
            "sizes": "any",
            "type": "image/svg+xml"
        }
    ],
    "theme_color": "#000000",
    "background_color": "#ffffff",
    "display": "standalone"
}'''
        self._create_file(
            self.project_root / "site.webmanifest",
            manifest_content,
            "Created site.webmanifest"
        )
    
    def _get_fallback_template(self, template_name: str) -> str:
        """Get fallback template content when framework templates aren't available"""
        if template_name == "base.html":
            return self._get_base_template()
        elif template_name == "index.html":
            return self._get_index_template()
        elif template_name == "admin_login.html":
            return self._get_admin_login_template()
        elif template_name == "404.html":
            return self._get_404_template()
        elif template_name == "500.html":
            return self._get_500_template()
        return None
    
    def _get_base_template(self) -> str:
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}CREATESONLINE App{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/base.css">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav>
        <h1>CREATESONLINE</h1>
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/about">About</a></li>
        </ul>
    </nav>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <p>Powered by CREATESONLINE</p>
    </footer>
    
    <script src="/static/js/base.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
'''
    
    def _get_index_template(self) -> str:
        return '''{% extends "base.html" %}

{% block title %}Home - CREATESONLINE{% endblock %}

{% block content %}
<div class="container">
    <h1>Welcome to CREATESONLINE</h1>
    <p>Your AI-Native Web Framework is ready!</p>
    
    <div class="features">
        <div class="feature">
            <h3> Zero Setup</h3>
            <p>Everything works out of the box</p>
        </div>
        <div class="feature">
            <h3> AI-First</h3>
            <p>Built for intelligent applications</p>
        </div>
        <div class="feature">
            <h3> Fast</h3>
            <p>Pure Python async/await</p>
        </div>
    </div>
</div>
{% endblock %}
'''
    
    def _get_admin_login_template(self) -> str:
        return '''{% extends "base.html" %}

{% block title %}Admin Login - CREATESONLINE{% endblock %}

{% block content %}
<div class="login-container">
    <h1>Admin Login</h1>
    <p class="subtitle">Enter your credentials to access the admin panel</p>
    
    <form method="POST" action="/admin/login">
        <div class="form-group">
            <label for="username">Username</label>
            <input type="text" id="username" name="username" required>
        </div>
        
        <div class="form-group">
            <label for="password">Password</label>
            <input type="password" id="password" name="password" required>
        </div>
        
        <button type="submit">Sign In</button>
    </form>
    
    <div class="back-link">
        <a href="/">Back to Home</a>
    </div>
</div>
{% endblock %}
'''
    
    def _get_404_template(self) -> str:
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - Page Not Found</title>
    
    <link rel="icon" type="image/svg+xml" href="/favicon.svg">
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a; color: #ffffff; min-height: 100vh;
            display: flex; align-items: center; justify-content: center; padding: 20px;
        }
        .container {
            max-width: 600px; width: 100%; text-align: center;
            background: #1a1a1a; padding: 60px 40px; border-radius: 16px; border: 1px solid #2a2a2a;
        }
        .error-code {
            font-size: 8em; font-weight: 700;
            background: linear-gradient(135deg, #ffffff 0%, #666666 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 20px; line-height: 1;
        }
        h1 { font-size: 2em; margin-bottom: 15px; }
        p { color: #999999; font-size: 1.1em; margin-bottom: 40px; line-height: 1.6; }
        .btn {
            display: inline-block; padding: 15px 35px; background: #ffffff;
            color: #000000; text-decoration: none; border-radius: 8px;
            font-weight: 600; transition: all 0.3s ease;
        }
        .btn:hover { background: #f0f0f0; transform: translateY(-2px); }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-code">404</div>
        <h1>Page Not Found</h1>
        <p>The page you're looking for doesn't exist or has been moved.</p>
        <a href="/" class="btn">Go Home</a>
    </div>
</body>
</html>
'''

    def _get_500_template(self) -> str:
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>500 - Server Error</title>
    <link rel="icon" type="image/svg+xml" href="/favicon.svg">
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a; color: #ffffff; min-height: 100vh;
            display: flex; align-items: center; justify-content: center; padding: 20px;
        }
        .container {
            max-width: 640px; width: 100%; text-align: center;
            background: #1a1a1a; padding: 60px 40px; border-radius: 16px; border: 1px solid #2a2a2a;
        }
        .error-code {
            font-size: 7rem; font-weight: 700;
            background: linear-gradient(135deg, #ffffff 0%, #777777 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 18px; line-height: 1;
        }
        h1 { font-size: 2em; margin-bottom: 14px; }
        p { color: #9a9a9a; margin-bottom: 28px; line-height: 1.6; }
        .btn {
            display: inline-block; padding: 14px 26px; border-radius: 10px;
            background: #ffffff; color: #000; text-decoration: none; font-weight: 700;
            transition: all 0.2s ease;
        }
        .btn:hover { background: #f0f0f0; transform: translateY(-2px); }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-code">500</div>
        <h1>Internal Server Error</h1>
        <p>Something went wrong on our side. Please retry in a moment or head back to safety.</p>
        <a class="btn" href="/">Return home</a>
    </div>
</body>
</html>
'''
    
    def _get_guide_html(self) -> str:
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quick Start Guide - CREATESONLINE</title>
    <style>
        body { font-family: system-ui; max-width: 900px; margin: 0 auto; padding: 2rem; }
        h1 { color: #2563eb; }
        pre { background: #1e1e1e; color: #d4d4d4; padding: 1rem; border-radius: 8px; overflow-x: auto; }
        code { font-family: 'Courier New', monospace; }
    </style>
</head>
<body>
    <h1>Quick Start Guide</h1>
    <p>Welcome to CREATESONLINE! This guide will get you started in 5 minutes.</p>
    
    <h2>1. Installation</h2>
    <pre><code>pip install createsonline</code></pre>
    
    <h2>2. Create Your App</h2>
    <p>Just run <code>python main.py</code> and everything is automatically set up!</p>
    
    <h2>3. Add Custom Routes</h2>
    <p>Edit <code>routes.py</code> to add your own routes:</p>
    <pre><code>async def my_api(request):
    return {"data": "Hello World"}

urlpatterns.append(path('/api/data', my_api))</code></pre>
    
    <h2>4. Customize</h2>
    <p>All your files are upgrade-safe! Edit freely:</p>
    <ul>
        <li><code>main.py</code> - App configuration</li>
        <li><code>routes.py</code> - URL routes</li>
        <li><code>user_config.py</code> - Settings</li>
        <li><code>templates/</code> - HTML templates</li>
        <li><code>static/</code> - CSS, JS, images</li>
    </ul>
    
    <p><a href="/">← Back to Home</a></p>
</body>
</html>
'''
    
    def _get_examples_html(self) -> str:
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Examples - CREATESONLINE</title>
    <style>
        body { font-family: system-ui; max-width: 1000px; margin: 0 auto; padding: 2rem; }
        h1 { color: #2563eb; }
        .example { background: #f8f9fa; padding: 1.5rem; margin: 1rem 0; border-radius: 8px; }
        pre { background: #1e1e1e; color: #d4d4d4; padding: 1rem; border-radius: 8px; overflow-x: auto; }
        code { font-family: 'Courier New', monospace; }
    </style>
</head>
<body>
    <h1>Code Examples</h1>
    
    <div class="example">
        <h3>1. Simple API Endpoint</h3>
        <pre><code>async def get_users(request):
    return {"users": ["Alice", "Bob", "Charlie"]}

urlpatterns.append(path('/api/users', get_users))</code></pre>
    </div>
    
    <div class="example">
        <h3>2. POST Request Handler</h3>
        <pre><code>async def create_user(request):
    data = await request.json()
    return {"created": data, "id": 123}

urlpatterns.append(
    path('/api/users', create_user, methods=['POST'])
)</code></pre>
    </div>
    
    <div class="example">
        <h3>3. Serve HTML Template</h3>
        <pre><code>async def about_page(request):
    # Return HTML template
    return render_template('about.html')

urlpatterns.append(path('/about', about_page))</code></pre>
    </div>
    
    <p><a href="/">← Back to Home</a></p>
</body>
</html>
'''
    
    def _get_readme_content(self) -> str:
        return '''# My CREATESONLINE Application

> ** UPGRADE-SAFE PROJECT** - All customizations are preserved during framework upgrades!

## Quick Start

```bash
# Install
pip install createsonline

# Run
python main.py

# Visit
http://localhost:8000
```

## Project Structure

```
your-project/
├── main.py               Your app bootstrap (SAFE TO EDIT)
├── routes.py             Your URL routes (SAFE TO EDIT)
├── user_config.py        Your settings (SAFE TO EDIT)
├── templates/            Your HTML templates (SAFE TO EDIT)
└── static/               Your CSS/JS/images (SAFE TO EDIT)
```

## Add Custom Routes

Edit `routes.py`:

```python
async def my_view(request):
    return {"message": "Hello!"}

urlpatterns.append(path('/custom', my_view))
```

## Upgrade Framework

```bash
pip install --upgrade createsonline
# Your files are automatically preserved! ✨
```

## Documentation

- Quick Start: `/static/guide.html`
- Examples: `/static/examples.html`
- GitHub: https://github.com/meahmedh/createsonline
'''


def auto_discover_routes(app):
    """
    Automatically discover and register routes from routes.py
    
    This function is called by main.py to register all user routes.
    Routes from routes.py OVERRIDE any routes defined elsewhere.
    It protects against errors - silent by default.
    """
    import logging
    logger = logging.getLogger("createsonline")
    
    try:
        from routes import urlpatterns
        
        registered = 0
        for route in urlpatterns:
            for method in route.methods:
                decorator = getattr(app, method.lower())
                handler = route.handler
                
                # Handle class-based views
                if hasattr(handler, 'dispatch'):
                    instance = handler() if callable(handler) else handler
                    async def view_wrapper(request, instance=instance):
                        return await instance.dispatch(request)
                    # Force override - routes.py takes priority
                    route_key = f"{method}:{route.path}"
                    if route_key in app.routes:
                        logger.debug(f"Overriding route: {route_key}")
                    decorator(route.path)(view_wrapper)
                else:
                    # Force override - routes.py takes priority  
                    route_key = f"{method}:{route.path}"
                    if route_key in app.routes:
                        logger.debug(f"Overriding route: {route_key}")
                    decorator(route.path)(handler)
                
                registered += 1
        
        # Register custom 404 handler if exists
        try:
            from routes import not_found
            app.routes['not_found'] = not_found
        except ImportError:
            pass
        
        # Silent success - routes registered
        logger.debug(f"Auto-discovered {registered} routes from routes.py")
        return True
        
    except ImportError:
        # No routes.py found - silent, use defaults
        return False
    except Exception as e:
        # Error loading routes - log but don't crash
        logger.warning(f"Error loading routes: {e}")
        return False


def init_project_if_needed(project_root: Path = None, verbose: bool = False):
    """
    Initialize project structure if needed.
    Called automatically when the app starts.
    Silent by default - only shows messages if verbose=True.
    
    Args:
        project_root: Root directory for the project (default: current directory)
        verbose: If True, print progress messages
    """
    project_root = project_root or Path.cwd()
    
    # Check if project is already initialized
    main_py = project_root / "main.py"
    routes_py = project_root / "routes.py"
    
    # Always create missing static assets (favicon, logo, manifest)
    initializer = ProjectInitializer(project_root)
    initializer.verbose = verbose
    initializer._create_directories()
    
    # ONE-TIME: Clean up legacy v0.1.1 main.py (v0.1.28 only)
    initializer._cleanup_legacy_main_py()
    
    initializer._ensure_static_files()
    initializer._ensure_templates()  # Always copy missing templates!
    
    # Always ensure routes.py exists (even if main.py exists from old version)
    if not routes_py.exists():
        initializer._ensure_routes_py()
    
    # If neither main.py nor routes.py exists, this is a new project
    if not main_py.exists():
        if verbose:
            print("\nWelcome to CREATESONLINE!")
            print("Setting up your project structure...")
        
        result = initializer.initialize(verbose=verbose)
        
        if verbose:
            print("\nNext steps:")
            print("   1. Edit routes.py to add your custom routes")
            print("   2. Customize templates/ and static/ folders")
            print("   3. Run: python main.py")
            print("\nHappy coding!\n")
        
        return result
    
    return {"success": True, "already_initialized": True}
