# createsonline/admin/__init__.py
from .interface import AdminSite, ModelAdmin

# Create default admin site
admin_site = AdminSite(name='admin')

__all__ = ['AdminSite', 'ModelAdmin', 'admin_site']