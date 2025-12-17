"""
CREATESONLINE API Documentation Generator

Generates beautiful HTML API documentation from route definitions.
"""
import json
from datetime import datetime
import platform
import sys
from typing import Dict, Any


class APIDocumentationGenerator:
    """Generate HTML API documentation for CREATESONLINE applications"""

    def __init__(self, app):
        self.app = app

    def generate_beautiful_api_docs(self):
        """Generate beautiful HTML API documentation with dynamic backend data"""
        spec = self._build_api_spec()
        html_content = self._render_html_template(spec)
        return self._create_html_response(html_content)

    def _build_api_spec(self) -> Dict[str, Any]:
        """Build OpenAPI specification"""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.app.title,
                "description": self.app.description,
                "version": self.app.version,
                "x-framework": "CREATESONLINE",
                "x-ai-enabled": len(self.app._ai_features) > 0,
                "x-mode": "internal",
                "x-timestamp": datetime.utcnow().isoformat(),
                "x-python-version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "x-platform": platform.system(),
                "x-architecture": platform.machine()
            },
            "servers": [
                {
                    "url": "/",
                    "description": "CREATESONLINE Development Server",
                    "variables": {
                        "protocol": {"default": "http", "enum": ["http", "https"]},
                        "host": {"default": "127.0.0.1:8000"}
                    }
                }
            ],
            "paths": self._generate_enhanced_api_paths(),
            "components": {
                "schemas": self._generate_api_schemas(),
                "securitySchemes": {
                    "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
                    "BearerAuth": {"type": "http", "scheme": "bearer"}
                }
            },
            "x-system-info": {
                "framework": "CREATESONLINE",
                "mode": "AI-Native",
                "features": self.app._ai_features,
                "total_routes": len(self.app._internal_routes),
                "ai_routes": len([r for r in self.app._internal_routes.keys() if 'ai' in r.lower()]),
                "admin_routes": len([r for r in self.app._internal_routes.keys() if 'admin' in r.lower()]),
                "startup_time": datetime.utcnow().isoformat(),
                "health_status": "operational",
                "debug_mode": self.app.debug
            }
        }

    def _generate_enhanced_api_paths(self) -> Dict[str, Any]:
        """Generate OpenAPI paths from registered routes"""
        paths = {}
        for path in self.app._internal_routes.keys():
            route_info = self.app._internal_routes[path]
            method = route_info.get('method', 'GET').lower()

            if path not in paths:
                paths[path] = {}

            paths[path][method] = {
                "summary": self._get_route_description(path, method),
                "tags": self._get_route_tags(path),
                "parameters": self._get_route_parameters(path),
                "responses": {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "example": self._get_example_response(path, method)
                            }
                        }
                    }
                },
                "x-code-samples": self._generate_code_samples(path, method)
            }

        return paths

    def _get_route_description(self, path: str, method: str) -> str:
        """Get route description"""
        if 'admin' in path:
            return "Admin interface"
        elif 'health' in path:
            return "Health check endpoint"
        elif 'framework' in path:
            return "Framework information"
        return f"{method.upper()} {path}"

    def _get_route_tags(self, path: str) -> list:
        """Get route tags"""
        tags = []
        if 'admin' in path:
            tags.append('Admin')
        if 'ai' in path:
            tags.append('AI')
        if not tags:
            tags.append('API')
        return tags

    def _get_route_parameters(self, path: str) -> list:
        """Extract path parameters"""
        import re
        params = []
        pattern = r'\{([^}]+)\}'
        for match in re.finditer(pattern, path):
            param_name = match.group(1)
            params.append({
                "name": param_name,
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "description": f"The {param_name} parameter"
            })
        return params

    def _get_example_response(self, path: str, method: str) -> Dict[str, Any]:
        """Generate example response"""
        return {
            "status": "success",
            "data": f"Response from {method.upper()} {path}",
            "timestamp": datetime.utcnow().isoformat()
        }

    def _generate_api_schemas(self) -> Dict[str, Any]:
        """Generate OpenAPI schemas"""
        return {
            "Error": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "message": {"type": "string"},
                    "code": {"type": "integer"}
                }
            },
            "Success": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "data": {"type": "object"},
                    "timestamp": {"type": "string"}
                }
            }
        }

    def _generate_code_samples(self, path: str, method: str) -> list:
        """Generate code samples for endpoint"""
        base_url = "http://localhost:8000"
        return [
            {
                "lang": "curl",
                "source": f'curl -X {method.upper()} "{base_url}{path}" \
  -H "Accept: application/json"'
            },
            {
                "lang": "javascript",
                "source": f'fetch("{base_url}{path}", {{\n  method: "{method.upper()}",\n  headers: {{"Accept": "application/json"}}\n}})'
            },
            {
                "lang": "python",
                "source": f'import requests\nresponse = requests.{method.lower()}("{base_url}{path}")\nprint(response.json())'
            }
        ]

    def _render_html_template(self, spec: Dict[str, Any]) -> str:
        """Render HTML documentation template"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.app.title} - API Documentation</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');
        :root {{
            --bg: #050608;
            --panel: #0b0d12;
            --card: #0f1118;
            --line: #1b1f2a;
            --text: #f6f7fb;
            --muted: #9ca3af;
            --accent: #ffffff;
            --radius: 18px;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
            background:
                radial-gradient(circle at 20% 20%, rgba(255,255,255,0.05), transparent 28%),
                radial-gradient(circle at 80% 0%, rgba(255,255,255,0.07), transparent 30%),
                linear-gradient(160deg, #050608 0%, #0c0d12 45%, #050608 100%);
            color: var(--text);
            min-height: 100vh;
            line-height: 1.6;
        }}
        .page {{ max-width: 1180px; margin: 0 auto; padding: 48px 22px 64px; }}
        .hero {{ margin-bottom: 28px; }}
        .eyebrow {{ display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px; border-radius: 999px; border: 1px solid var(--line); background: rgba(255,255,255,0.06); color: var(--muted); letter-spacing: 0.08em; text-transform: uppercase; font-size: 0.85rem; }}
        h1 {{ font-size: clamp(2.4rem, 4vw, 3rem); margin: 16px 0 12px; letter-spacing: -0.02em; }}
        .lede {{ color: var(--muted); font-size: 1.05rem; max-width: 760px; }}
        .meta {{ display: flex; gap: 10px; flex-wrap: wrap; margin: 16px 0 20px; }}
        .badge {{ padding: 8px 12px; border-radius: 999px; border: 1px solid var(--line); background: rgba(255,255,255,0.04); color: var(--text); font-weight: 600; }}
        .actions {{ display: flex; gap: 10px; flex-wrap: wrap; }}
        .button {{ padding: 12px 16px; border-radius: 12px; border: 1px solid var(--line); background: rgba(255,255,255,0.05); color: var(--text); text-decoration: none; font-weight: 700; transition: all .2s ease; }}
        .button:hover {{ border-color: rgba(255,255,255,0.35); transform: translateY(-1px); }}
        .button.primary {{ background: var(--text); color: #0b0d12; border-color: transparent; }}
        .grid {{ display: grid; gap: 14px; }}
        .grid.two {{ grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }}
        .card {{ background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px; box-shadow: 0 18px 38px rgba(0,0,0,0.45); }}
        .card-title {{ font-weight: 700; margin-bottom: 8px; }}
        .summary {{ color: var(--muted); margin: 6px 0 10px; }}
        .endpoint {{ border: 1px solid var(--line); border-radius: 14px; padding: 14px; margin-bottom: 12px; background: rgba(255,255,255,0.02); }}
        .endpoint-head {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-bottom: 8px; }}
        .method {{ padding: 6px 10px; border-radius: 10px; font-weight: 700; border: 1px solid var(--line); min-width: 64px; text-align: center; }}
        .method.get {{ background: rgba(255,255,255,0.12); }}
        .method.post {{ background: rgba(255,255,255,0.08); }}
        .method.put {{ background: rgba(255,255,255,0.06); }}
        .method.delete {{ background: rgba(255,255,255,0.04); }}
        .path {{ font-family: 'JetBrains Mono', 'Courier New', monospace; }}
        .code {{ background: #0c0e15; border: 1px solid var(--line); border-radius: 10px; padding: 10px; font-family: 'JetBrains Mono', 'Courier New', monospace; color: var(--text); overflow-x: auto; font-size: 0.9rem; }}
        .footer {{ margin-top: 20px; color: var(--muted); font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="page">
        <header class="hero">
            <div class="eyebrow">API Docs</div>
            <h1>{self.app.title}</h1>
            <p class="lede">{self.app.description}</p>
            <div class="meta">
                <span class="badge">Version {self.app.version}</span>
                <span class="badge">{spec['x-system-info']['total_routes']} endpoints</span>
                <span class="badge">Python {spec['info']['x-python-version']}</span>
            </div>
            <div class="actions">
                <a class="button primary" href="/">Home</a>
                <a class="button" href="/admin">Admin</a>
                <a class="button" href="/static/guide.html">Guide</a>
            </div>
        </header>

        <div class="grid two" style="margin-bottom:18px;">
            <div class="card">
                <div class="card-title">AI features</div>
                <p class="summary">Enabled: {', '.join(spec['x-system-info']['features']) if spec['x-system-info']['features'] else 'None configured'}</p>
            </div>
            <div class="card">
                <div class="card-title">Mode</div>
                <p class="summary">Internal ASGI / Monochrome UI / Upgrade-safe assets</p>
            </div>
        </div>

        <div class="card">
            <div class="card-title">Endpoints</div>
            <div class="endpoint-list">
                {self._render_endpoints_html(spec)}
            </div>
        </div>

        <p class="footer">Icons &amp; manifest served from /static/image and /static/images for consistent branding.</p>
    </div>
</body>
</html>
"""

    def _render_endpoints_html(self, spec: Dict[str, Any]) -> str:
        """Render endpoints in HTML"""
        html = ""
        for path, methods in spec.get('paths', {}).items():
            for method, details in methods.items():
                if method.startswith('x-'):
                    continue
                tags = ', '.join(details.get('tags', []) or ['API'])
                summary = details.get('summary', 'No description')
                method_class = method.lower()
                curl_sample = f"curl -X {method.upper()} \\\"{path}\\\" -H 'Accept: application/json'"
                html += f"""
                <div class="endpoint">
                    <div class="endpoint-head">
                        <span class="method {method_class}">{method.upper()}</span>
                        <span class="path">{path}</span>
                        <span class="badge">{tags}</span>
                    </div>
                    <p class="summary">{summary}</p>
                    <div class="code">{curl_sample}</div>
                </div>
                """
        return html

    def _create_html_response(self, content: str):
        """Create HTML response object"""
        class HTMLResponse:
            def __init__(self, content, status_code=200, headers=None):
                self.content = content
                self.status_code = status_code
                self.headers = headers or {'content-type': 'text/html'}

        return HTMLResponse(content)
