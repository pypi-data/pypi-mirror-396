"""
PyX API Documentation
Zen Mode access for OpenAPI/Swagger configuration.
"""
from typing import List, Dict, Any, Optional

class ZenDocs:
    """
    Zen Mode Documentation Configuration.
    
    Usage:
        from pyx import docs
        
        # Configure API Docs
        docs.configure(
            app,
            title="My Super API",
            version="1.0.0",
            description="API documentation for My Super App",
            terms_of_service="http://example.com/terms/",
            contact={"name": "Support", "email": "help@example.com"},
            license_info={"name": "MIT"}
        )
        
        # Enable/Disable
        docs.enable(app)
        docs.disable(app)
    """
    
    def configure(
        self,
        app,
        title: str = None,
        version: str = None,
        description: str = None,
        openapi_url: str = "/openapi.json",
        docs_url: str = "/docs",
        redoc_url: str = "/redoc",
        terms_of_service: str = None,
        contact: Dict[str, str] = None,
        license_info: Dict[str, str] = None,
        tags: List[Dict[str, Any]] = None
    ):
        """
        Configure OpenAPI documentation settings.
        
        Args:
            app: PyX App instance
            title: API Title
            version: API Version
            description: Markup description
            ...
        """
        # Access underlying FastAPI app
        # NOTE: app might be PyX App wrapper or FastAPI instance directly
        api = getattr(app, 'api', app)
        
        if title: api.title = title
        if version: api.version = version
        if description: api.description = description
        if openapi_url: api.openapi_url = openapi_url
        if docs_url: api.docs_url = docs_url
        if redoc_url: api.redoc_url = redoc_url
        if terms_of_service: api.terms_of_service = terms_of_service
        if contact: api.contact = contact
        if license_info: api.license_info = license_info
        if tags: api.openapi_tags = tags
        
        return self
        
    def disable(self, app):
        """Disable API documentation"""
        api = getattr(app, 'api', app)
        api.openapi_url = None
        api.docs_url = None
        api.redoc_url = None
        return self

    def enable(self, app, docs_url: str = "/docs", openapi_url: str = "/openapi.json"):
        """Enable API documentation"""
        api = getattr(app, 'api', app)
        api.docs_url = docs_url
        api.openapi_url = openapi_url
        return self


# Zen Mode instance
docs = ZenDocs()


__all__ = ['docs', 'ZenDocs']
