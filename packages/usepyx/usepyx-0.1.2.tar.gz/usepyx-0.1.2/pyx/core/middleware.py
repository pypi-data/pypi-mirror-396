"""
PyX Middleware System
Lapisan pemrosesan antara Request dan Controller.
"""
from typing import Callable, List, Optional
from functools import wraps
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pyx")


class MiddlewareStack:
    """
    Manages middleware execution order.
    Middleware are executed in FIFO order (first added, first executed).
    """
    
    def __init__(self):
        self.middlewares: List[Callable] = []
    
    def add(self, middleware: Callable):
        """Add middleware to the stack"""
        self.middlewares.append(middleware)
    
    async def execute(self, request, call_next):
        """Execute all middlewares in order"""
        # Build middleware chain
        async def chain(index, req):
            if index >= len(self.middlewares):
                return await call_next(req)
            
            middleware = self.middlewares[index]
            return await middleware(req, lambda r: chain(index + 1, r))
        
        return await chain(0, request)


# ==========================================
# BUILT-IN MIDDLEWARES
# ==========================================

class LoggingMiddleware:
    """
    Logs every request with timestamp, method, path, and response time.
    
    Usage:
        app.use(LoggingMiddleware())
    """
    
    async def __call__(self, request, call_next):
        start_time = time.time()
        
        # Log request
        method = request.scope.get("method", "WS")
        path = request.scope.get("path", "/")
        
        # Process request
        response = await call_next(request)
        
        # Calculate time
        process_time = (time.time() - start_time) * 1000
        
        # Log with timing
        logger.info(f"[{method}] {path} - {process_time:.2f}ms")
        
        return response


class CORSMiddleware:
    """
    Cross-Origin Resource Sharing middleware.
    
    Usage:
        app.use(CORSMiddleware(origins=["http://localhost:3000"]))
    """
    
    def __init__(
        self,
        origins: List[str] = ["*"],
        methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        headers: List[str] = ["*"]
    ):
        self.origins = origins
        self.methods = methods
        self.headers = headers
    
    async def __call__(self, request, call_next):
        response = await call_next(request)
        
        # Add CORS headers
        origin = request.headers.get("origin", "*")
        if "*" in self.origins or origin in self.origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = ", ".join(self.methods)
            response.headers["Access-Control-Allow-Headers"] = ", ".join(self.headers)
        
        return response


class RateLimitMiddleware:
    """
    Rate limiting middleware to prevent abuse.
    
    Usage:
        app.use(RateLimitMiddleware(max_requests=100, window_seconds=60))
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # IP -> [(timestamp, count)]
    
    def _get_client_ip(self, request) -> str:
        """Extract client IP from request"""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, ip: str) -> bool:
        """Check if IP has exceeded rate limit"""
        current_time = time.time()
        
        # Clean old entries
        if ip in self.requests:
            self.requests[ip] = [
                (t, c) for t, c in self.requests[ip]
                if current_time - t < self.window_seconds
            ]
        
        # Count requests in window
        if ip not in self.requests:
            self.requests[ip] = []
        
        total_requests = sum(c for _, c in self.requests[ip])
        
        if total_requests >= self.max_requests:
            return True
        
        # Add current request
        self.requests[ip].append((current_time, 1))
        return False
    
    async def __call__(self, request, call_next):
        ip = self._get_client_ip(request)
        
        if self._is_rate_limited(ip):
            from fastapi.responses import JSONResponse
            return JSONResponse(
                {"error": "Rate limit exceeded. Try again later."},
                status_code=429
            )
        
        return await call_next(request)


class AuthMiddleware:
    """
    Authentication middleware for protected routes.
    
    Usage:
        app.use(AuthMiddleware(
            protected_paths=["/dashboard", "/admin"],
            login_path="/login"
        ))
    """
    
    def __init__(
        self,
        protected_paths: List[str] = [],
        login_path: str = "/login",
        exclude_paths: List[str] = []
    ):
        self.protected_paths = protected_paths
        self.login_path = login_path
        self.exclude_paths = exclude_paths + [login_path, "/register", "/assets"]
    
    def _is_protected(self, path: str) -> bool:
        """Check if path requires authentication"""
        # Check exclusions first
        for excluded in self.exclude_paths:
            if path.startswith(excluded):
                return False
        
        # Check if any protected path matches
        for protected in self.protected_paths:
            if path.startswith(protected):
                return True
        
        return False
    
    async def __call__(self, request, call_next):
        path = request.scope.get("path", "/")
        
        if self._is_protected(path):
            # Check for session token in cookies or headers
            from ..lib.auth import auth
            
            # Try to get token from cookie
            cookies = request.cookies
            token = cookies.get("pyx_session")
            
            if not token:
                # Try header
                token = request.headers.get("Authorization", "").replace("Bearer ", "")
            
            if not token or not auth.get_user(token):
                from fastapi.responses import RedirectResponse
                return RedirectResponse(url=self.login_path, status_code=302)
        
        return await call_next(request)


class ErrorHandlerMiddleware:
    """
    Global error handler middleware.
    Catches all exceptions and returns formatted error response.
    
    Usage:
        app.use(ErrorHandlerMiddleware(debug=True))
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
    
    async def __call__(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            import traceback
            
            logger.error(f"Error: {str(e)}")
            if self.debug:
                traceback.print_exc()
            
            from fastapi.responses import JSONResponse
            
            error_response = {"error": str(e)}
            if self.debug:
                error_response["traceback"] = traceback.format_exc()
            
            return JSONResponse(error_response, status_code=500)


class CSRFMiddleware:
    """
    CSRF (Cross-Site Request Forgery) protection middleware.
    
    Usage:
        app.use(CSRFMiddleware())
        
    How it works:
    - Generates a CSRF token for each session
    - Validates token on POST/PUT/DELETE requests
    - Token can be passed via:
      - Header: X-CSRF-Token
      - Form field: _csrf_token
      - Cookie: pyx_csrf (for SPA)
    """
    
    def __init__(
        self,
        exempt_paths: List[str] = [],
        cookie_name: str = "pyx_csrf",
        header_name: str = "X-CSRF-Token",
        field_name: str = "_csrf_token"
    ):
        self.exempt_paths = exempt_paths + ["/api/", "/ws"]
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.field_name = field_name
        self.tokens = {}  # session_id -> token
    
    def _is_exempt(self, path: str, method: str) -> bool:
        """Check if path is exempt from CSRF"""
        # GET, HEAD, OPTIONS don't need CSRF
        if method in ["GET", "HEAD", "OPTIONS"]:
            return True
        
        for exempt in self.exempt_paths:
            if path.startswith(exempt):
                return True
        return False
    
    def _generate_token(self) -> str:
        """Generate a new CSRF token"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _get_session_id(self, request) -> str:
        """Get session ID from request"""
        return request.cookies.get("pyx_session", "anonymous")
    
    def _validate_token(self, request, token: str) -> bool:
        """Validate CSRF token"""
        session_id = self._get_session_id(request)
        expected = self.tokens.get(session_id)
        return expected and token == expected
    
    async def __call__(self, request, call_next):
        path = request.scope.get("path", "/")
        method = request.scope.get("method", "GET")
        
        # Generate token for session if not exists
        session_id = self._get_session_id(request)
        if session_id not in self.tokens:
            self.tokens[session_id] = self._generate_token()
        
        # Skip exempt paths
        if self._is_exempt(path, method):
            response = await call_next(request)
            # Set CSRF cookie on response
            response.set_cookie(
                self.cookie_name,
                self.tokens[session_id],
                httponly=False,  # JS needs access
                samesite="strict"
            )
            return response
        
        # Validate CSRF token for state-changing requests
        token = None
        
        # Try header first
        token = request.headers.get(self.header_name)
        
        # Try cookie
        if not token:
            token = request.cookies.get(self.cookie_name)
        
        if not self._validate_token(request, token):
            from fastapi.responses import JSONResponse
            logger.warning(f"CSRF validation failed for {path}")
            return JSONResponse(
                {"error": "CSRF token validation failed"},
                status_code=403
            )
        
        response = await call_next(request)
        return response



# ==========================================
# DECORATOR MIDDLEWARES
# ==========================================

def protected(login_redirect: str = "/login"):
    """
    Decorator to protect individual routes.
    
    Usage:
        @protected()
        def dashboard_page():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from ..lib.auth import auth
            
            if not auth.is_authenticated():
                # For now, just print warning
                # Full redirect requires request context
                print(f"[PyX] Access denied: Route requires authentication")
                return None
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: str):
    """
    Decorator to require specific role.
    
    Usage:
        @require_role("admin")
        def admin_page():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from ..lib.auth import auth
            
            user = auth.current_user()
            if not user:
                print(f"[PyX] Access denied: Not authenticated")
                return None
            
            if user.role != role:
                print(f"[PyX] Access denied: Requires role '{role}'")
                return None
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_permission(action: str):
    """
    Decorator to require specific permission (RBAC).
    
    Usage:
        @require_permission("create")
        def create_product():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from ..lib.auth import auth
            
            user = auth.current_user()
            if not user:
                print(f"[PyX] Access denied: Not authenticated")
                return None
            
            if not user.can(action):
                print(f"[PyX] Access denied: Missing permission '{action}'")
                return None
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
