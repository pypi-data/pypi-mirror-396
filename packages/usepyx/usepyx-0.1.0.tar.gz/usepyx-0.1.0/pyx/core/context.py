"""
PyX Router Context
Provides access to current route information within handlers.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import contextvars

# Context variable to store current request info
_current_request: contextvars.ContextVar[Optional['RequestContext']] = contextvars.ContextVar('current_request', default=None)


@dataclass
class PageInfo:
    """Information about the current page/route"""
    path: str = ""
    params: Dict[str, str] = field(default_factory=dict)
    query: Dict[str, str] = field(default_factory=dict)
    full_url: str = ""
    method: str = "GET"


@dataclass  
class SessionInfo:
    """Information about the current session"""
    session_id: Optional[str] = None
    user_id: Optional[int] = None
    is_authenticated: bool = False


@dataclass
class RequestContext:
    """Full context for the current request"""
    page: PageInfo = field(default_factory=PageInfo)
    session: SessionInfo = field(default_factory=SessionInfo)
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)


class RouterContext:
    """
    Provides access to current route/request information.
    
    Usage in handlers:
        from pyx import router
        
        def my_handler():
            current_path = router.page.path
            user_id = router.page.params.get("id")
            search = router.page.query.get("q")
            
            if router.session.is_authenticated:
                ...
    """
    
    @property
    def page(self) -> PageInfo:
        """Get current page information"""
        ctx = _current_request.get()
        return ctx.page if ctx else PageInfo()
    
    @property
    def session(self) -> SessionInfo:
        """Get current session information"""
        ctx = _current_request.get()
        return ctx.session if ctx else SessionInfo()
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get current request headers"""
        ctx = _current_request.get()
        return ctx.headers if ctx else {}
    
    @property
    def cookies(self) -> Dict[str, str]:
        """Get current request cookies"""
        ctx = _current_request.get()
        return ctx.cookies if ctx else {}
    
    @staticmethod
    def set_context(ctx: RequestContext):
        """Set the current request context (called by framework)"""
        _current_request.set(ctx)
    
    @staticmethod
    def clear_context():
        """Clear the current request context"""
        _current_request.set(None)
    
    @staticmethod
    def from_request(request) -> RequestContext:
        """
        Create RequestContext from a FastAPI/Starlette Request object.
        Called internally by the framework.
        """
        # Extract path params
        path_params = dict(request.path_params) if hasattr(request, 'path_params') else {}
        
        # Extract query params
        query_params = dict(request.query_params) if hasattr(request, 'query_params') else {}
        
        # Extract headers
        headers = dict(request.headers) if hasattr(request, 'headers') else {}
        
        # Extract cookies
        cookies = dict(request.cookies) if hasattr(request, 'cookies') else {}
        
        # Build page info
        page = PageInfo(
            path=str(request.url.path) if hasattr(request, 'url') else "",
            params=path_params,
            query=query_params,
            full_url=str(request.url) if hasattr(request, 'url') else "",
            method=request.method if hasattr(request, 'method') else "GET"
        )
        
        # Build session info (will be populated by auth middleware)
        session = SessionInfo()
        
        return RequestContext(
            page=page,
            session=session,
            headers=headers,
            cookies=cookies
        )


# Global instance for easy import
router = RouterContext()
