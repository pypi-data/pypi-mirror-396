# createsonline/templates.py
"""
Template Rendering System with Jinja2 Support

Supports both simple built-in engine and Jinja2 for advanced features.
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("createsonline")

# Try to import Jinja2
try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False
    logger.warning("Jinja2 not installed - falling back to basic template engine")


class TemplateEngine:
    """
    Simple template engine supporting:
    - {% extends "base.html" %}
    - {% block name %}...{% endblock %}
    - {{ variable }}
    - {% for item in items %}...{% endfor %}
    - {% if condition %}...{% endif %}
    """
    
    def __init__(self, template_dirs: list = None):
        """
        Initialize template engine
        
        Args:
            template_dirs: List of directories to search for templates
        """
        if template_dirs is None:
            template_dirs = [Path.cwd() / "templates"]
        
        self.template_dirs = [Path(d) for d in template_dirs]
        self._template_cache = {}
    
    def find_template(self, name: str) -> Optional[Path]:
        """Find template file in template directories"""
        for template_dir in self.template_dirs:
            template_path = template_dir / name
            if template_path.exists():
                return template_path
        return None
    
    def load_template(self, name: str) -> str:
        """Load template content from file"""
        if name in self._template_cache:
            return self._template_cache[name]
        
        template_path = self.find_template(name)
        if not template_path:
            raise FileNotFoundError(f"Template not found: {name}")
        
        content = template_path.read_text(encoding='utf-8')
        self._template_cache[name] = content
        return content
    
    def render(self, template_name: str, context: Dict[str, Any] = None) -> str:
        """
        Render a template with context
        
        Args:
            template_name: Name of the template file
            context: Dictionary of variables to pass to template
            
        Returns:
            Rendered HTML string
        """
        if context is None:
            context = {}
        
        try:
            content = self.load_template(template_name)
            
            # Handle {% extends "..." %}
            extends_match = re.search(r'{%\s*extends\s+["\'](.+?)["\']\s*%}', content)
            if extends_match:
                parent_name = extends_match.group(1)
                content = self._handle_extends(content, parent_name, context)
            
            # Render the final content
            return self._render_content(content, context)
            
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            return f"<html><body><h1>Template Error</h1><p>{str(e)}</p></body></html>"
    
    def _handle_extends(self, child_content: str, parent_name: str, context: Dict[str, Any]) -> str:
        """Handle template inheritance with {% extends %}"""
        # Load parent template
        parent_content = self.load_template(parent_name)
        
        # Extract blocks from child template
        child_blocks = self._extract_blocks(child_content)
        
        # Replace blocks in parent template
        result = parent_content
        for block_name, block_content in child_blocks.items():
            # Find block in parent and replace
            pattern = r'{%\s*block\s+' + re.escape(block_name) + r'\s*%}.*?{%\s*endblock\s*%}'
            replacement = f'{{% block {block_name} %}}{block_content}{{% endblock %}}'
            result = re.sub(pattern, replacement, result, flags=re.DOTALL)
        
        return result
    
    def _extract_blocks(self, content: str) -> Dict[str, str]:
        """Extract all {% block name %}...{% endblock %} from template"""
        blocks = {}
        pattern = r'{%\s*block\s+(\w+)\s*%}(.*?){%\s*endblock\s*%}'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            block_name = match.group(1)
            block_content = match.group(2)
            blocks[block_name] = block_content
        
        return blocks
    
    def _render_content(self, content: str, context: Dict[str, Any]) -> str:
        """Render template content with context"""
        # Remove {% extends %} tag if still present
        content = re.sub(r'{%\s*extends\s+["\'](.+?)["\']\s*%}', '', content)
        
        # Render {% block %} tags (remove block markers, keep content)
        content = re.sub(r'{%\s*block\s+\w+\s*%}', '', content)
        content = re.sub(r'{%\s*endblock\s*%}', '', content)
        
        # Render {{ variable }} tags
        def replace_var(match):
            var_name = match.group(1).strip()
            return str(context.get(var_name, ''))
        
        content = re.sub(r'{{\s*(.+?)\s*}}', replace_var, content)
        
        return content


# Global template engine instance
_template_engine = None
_jinja2_env = None


def get_jinja2_environment():
    """Get or create Jinja2 environment"""
    global _jinja2_env
    
    if _jinja2_env is None and HAS_JINJA2:
        # Auto-discover template directories
        template_dirs = []
        
        # Check current working directory
        cwd = Path.cwd()
        if (cwd / "templates").exists():
            template_dirs.append(str(cwd / "templates"))
        
        # Check createsonline package templates
        pkg_templates = Path(__file__).parent / "templates"
        if pkg_templates.exists():
            template_dirs.append(str(pkg_templates))
        
        _jinja2_env = Environment(
            loader=FileSystemLoader(template_dirs),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    return _jinja2_env


def get_template_engine() -> TemplateEngine:
    """Get or create the global template engine instance"""
    global _template_engine
    
    if _template_engine is None:
        # Auto-discover template directories
        template_dirs = []
        
        # Check current working directory
        cwd = Path.cwd()
        if (cwd / "templates").exists():
            template_dirs.append(cwd / "templates")
        
        # Check createsonline package templates
        pkg_templates = Path(__file__).parent / "templates"
        if pkg_templates.exists():
            template_dirs.append(pkg_templates)
        
        _template_engine = TemplateEngine(template_dirs)
    
    return _template_engine


def render_template(template_name: str, context: Dict[str, Any] = None) -> str:
    """
    Convenience function to render a template
    
    Uses Jinja2 if available, falls back to basic engine.
    
    Args:
        template_name: Name of the template file (e.g., "index.html")
        context: Dictionary of variables to pass to template
        
    Returns:
        Rendered HTML string
        
    Example:
        html = render_template("index.html", {"title": "Welcome"})
    """
    from createsonline import __version__
    
    # Auto-inject framework version into all template contexts
    if context is None:
        context = {}
    context.setdefault('CREATESONLINE_VERSION', __version__)
    
    # Use Jinja2 if available
    if HAS_JINJA2:
        try:
            env = get_jinja2_environment()
            if env:
                template = env.get_template(template_name)
                return template.render(context)
        except Exception as e:
            logger.error(f"Jinja2 rendering error: {e}")
            # Fall through to basic engine
    
    # Fallback to basic engine
    engine = get_template_engine()
    return engine.render(template_name, context)


def render_to_response(template_name: str, context: Dict[str, Any] = None):
    """
    Render template and return response tuple
    
    Args:
        template_name: Name of the template file
        context: Dictionary of variables to pass to template
        
    Returns:
        Tuple of (html_string, status_code, headers)
    """
    html = render_template(template_name, context)
    return html, 200, {'Content-Type': 'text/html; charset=utf-8'}


__all__ = [
    'TemplateEngine',
    'render_template',
    'render_to_response',
    'get_template_engine',
]
