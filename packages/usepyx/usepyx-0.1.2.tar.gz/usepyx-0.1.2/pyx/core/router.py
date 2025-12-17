"""
PyX Unified Router
Supports both manual and file-based routing in one system.
"""
import os
import re
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field


@dataclass
class Route:
    """Route definition"""
    path: str
    handler: Callable
    file_path: str = None
    is_dynamic: bool = False
    dynamic_params: List[str] = field(default_factory=list)
    is_api: bool = False
    method: str = "GET"
    layout: str = None
    middleware: List[Callable] = field(default_factory=list)


class Router:
    """
    Unified Router - supports both manual and file-based routing.
    
    Usage:
        # Create router
        router = Router()
        
        # Manual routing (Flask/FastAPI style)
        router.add("/", home_view)
        router.add("/about", about_view)
        
        # Or with decorator
        @router.page("/contact")
        def contact_page():
            return ui.div("Contact")
        
        # File-based routing (Next.js style)
        router.discover("pages")  # Auto-discover from pages/
        
        # Hybrid - both work together!
        router.add("/special", special_view)
        router.discover("pages")
        
        # Get all routes
        routes = router.routes
    """
    
    def __init__(self, prefix: str = ""):
        self.prefix = prefix.rstrip("/")
        self._routes: Dict[str, Route] = {}
        self._layouts: Dict[str, Callable] = {}
        self._middleware: List[Callable] = []
        self._api_routes: List[Tuple] = []
    
    # =========================================================================
    # MANUAL ROUTING (Flask/FastAPI style)
    # =========================================================================
    
    def add(self, path: str, handler: Callable, method: str = "GET", **kwargs) -> "Router":
        """
        Add a route manually.
        
        Usage:
            router.add("/", home_view)
            router.add("/api/users", get_users, method="GET")
        """
        full_path = self._normalize_path(path)
        
        # Parse dynamic params
        dynamic_params = re.findall(r':(\w+)', full_path)
        is_dynamic = len(dynamic_params) > 0
        
        route = Route(
            path=full_path,
            handler=handler,
            is_dynamic=is_dynamic,
            dynamic_params=dynamic_params,
            is_api=path.startswith("/api"),
            method=method,
            **kwargs
        )
        
        self._routes[full_path] = route
        return self
    
    def add_page(self, path: str, handler: Callable, **kwargs) -> "Router":
        """Alias for add() - for backward compatibility"""
        return self.add(path, handler, method="GET", **kwargs)
    
    def add_api(self, path: str, handler: Callable, method: str = "GET", **kwargs) -> "Router":
        """Add an API route"""
        if not path.startswith("/api"):
            path = f"/api{path}"
        return self.add(path, handler, method=method, is_api=True, **kwargs)
    
    def page(self, path: str, **kwargs):
        """
        Decorator for adding pages.
        
        Usage:
            @router.page("/about")
            def about():
                return ui.div("About")
        """
        def decorator(func):
            self.add(path, func, **kwargs)
            return func
        return decorator
    
    def api(self, path: str, method: str = "GET", **kwargs):
        """
        Decorator for API routes.
        
        Usage:
            @router.api("/users")
            def get_users():
                return {"users": [...]}
        """
        def decorator(func):
            self.add_api(path, func, method=method, **kwargs)
            return func
        return decorator
    
    # =========================================================================
    # FILE-BASED ROUTING (Next.js style)
    # =========================================================================
    
    def discover(self, pages_dir: str = "pages") -> "Router":
        """
        Auto-discover routes from file system.
        
        Directory structure:
            pages/
            ├── index.py          → /
            ├── about.py          → /about
            ├── blog/
            │   ├── index.py      → /blog
            │   └── [slug].py     → /blog/:slug
            └── api/
                └── users.py      → /api/users
        
        Usage:
            router.discover("pages")
        """
        pages_path = Path(pages_dir)
        
        if not pages_path.exists():
            print(f"⚠️  Pages directory '{pages_dir}' not found")
            return self
        
        print(f"📁 Discovering routes from {pages_dir}/")
        self._scan_directory(pages_path, pages_path, "")
        print(f"✅ Found {len(self._routes)} routes\n")
        
        return self
    
    def _scan_directory(self, base_path: Path, directory: Path, prefix: str):
        """Recursively scan directory for page files"""
        for item in sorted(directory.iterdir()):
            if item.name.startswith("_") or item.name.startswith("."):
                # Handle special files
                if item.name == "_layout.py":
                    self._load_layout(item, prefix)
                continue
            
            if item.is_dir():
                # Check for dynamic segment [param]
                if item.name.startswith("[") and item.name.endswith("]"):
                    param = item.name[1:-1]
                    new_prefix = f"{prefix}/:{param}"
                else:
                    new_prefix = f"{prefix}/{item.name}"
                
                self._scan_directory(base_path, item, new_prefix)
                
            elif item.suffix == ".py":
                self._register_file(base_path, item, prefix)
    
    def _register_file(self, base_path: Path, file: Path, prefix: str):
        """Register a page file as a route"""
        name = file.stem
        
        # Determine route path
        if name == "index":
            route_path = prefix or "/"
        elif name.startswith("[") and name.endswith("]"):
            param = name[1:-1]
            route_path = f"{prefix}/:{param}"
        else:
            route_path = f"{prefix}/{name}"
        
        # Normalize path
        route_path = self._normalize_path(route_path)
        
        # Check if API route
        is_api = route_path.startswith("/api")
        
        # Load handler
        try:
            handler = self._load_module(file)
            if handler:
                dynamic_params = re.findall(r':(\w+)', route_path)
                
                route = Route(
                    path=route_path,
                    handler=handler,
                    file_path=str(file),
                    is_dynamic=len(dynamic_params) > 0,
                    dynamic_params=dynamic_params,
                    is_api=is_api,
                )
                
                self._routes[route_path] = route
                rel_path = file.relative_to(base_path)
                print(f"   {rel_path} → {route_path}")
        
        except Exception as e:
            print(f"   ⚠️ Error loading {file}: {e}")
    
    def _load_module(self, file: Path) -> Optional[Callable]:
        """Load a Python module and extract handler"""
        spec = importlib.util.spec_from_file_location(file.stem, file)
        if not spec or not spec.loader:
            return None
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Look for handler function
        for func_name in ["page", "default", "view", "get", "handler"]:
            if hasattr(module, func_name):
                return getattr(module, func_name)
        
        return None
    
    def _load_layout(self, file: Path, prefix: str):
        """Load a layout file"""
        try:
            spec = importlib.util.spec_from_file_location("layout", file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, "layout"):
                    self._layouts[prefix or "/"] = module.layout
                    print(f"   📐 Layout: {prefix or '/'}")
        except Exception as e:
            print(f"   ⚠️ Error loading layout: {e}")
    
    # =========================================================================
    # ROUTE MATCHING
    # =========================================================================
    
    def match(self, path: str, method: str = "GET") -> Optional[Tuple[Route, Dict]]:
        """
        Match a path to a route.
        
        Returns:
            (Route, params) if matched, None otherwise
        """
        # Exact match first
        if path in self._routes:
            route = self._routes[path]
            if route.method == method or method == "GET":
                return (route, {})
        
        # Dynamic match
        for route_path, route in self._routes.items():
            if route.is_dynamic and (route.method == method or method == "GET"):
                params = self._match_dynamic(path, route_path, route.dynamic_params)
                if params is not None:
                    return (route, params)
        
        return None
    
    def _match_dynamic(self, path: str, pattern: str, params: List[str]) -> Optional[Dict]:
        """Match path against dynamic pattern"""
        regex_pattern = pattern
        for param in params:
            regex_pattern = regex_pattern.replace(f":{param}", f"(?P<{param}>[^/]+)")
        
        regex_pattern = f"^{regex_pattern}$"
        match = re.match(regex_pattern, path)
        
        if match:
            return match.groupdict()
        return None
    
    # =========================================================================
    # UTILITIES
    # =========================================================================
    
    def _normalize_path(self, path: str) -> str:
        """Normalize route path"""
        full_path = f"{self.prefix}{path}" if self.prefix else path
        full_path = full_path.replace("//", "/")
        if not full_path.startswith("/"):
            full_path = "/" + full_path
        return full_path
    
    @property
    def routes(self) -> Dict[str, Route]:
        """Get all routes"""
        return self._routes
    
    def get_routes_list(self) -> List[Dict]:
        """Get routes as list of dicts"""
        return [
            {
                "path": r.path,
                "method": r.method,
                "dynamic": r.is_dynamic,
                "api": r.is_api,
                "file": r.file_path,
            }
            for r in self._routes.values()
        ]
    
    def print_routes(self):
        """Print all routes"""
        print("\n📍 Routes:")
        for path, route in sorted(self._routes.items()):
            marker = "🔌" if route.is_api else "📄"
            dynamic = f" (params: {route.dynamic_params})" if route.is_dynamic else ""
            print(f"   {marker} {route.method:6} {path}{dynamic}")
        print()
    
    # =========================================================================
    # AUTO CRUD API (for models)
    # =========================================================================
    
    def crud(self, model_class, prefix: str = None):
        """
        Generate CRUD API endpoints for a model.
        
        Usage:
            router.crud(User)  # Creates /api/users endpoints
        """
        if prefix is None:
            name = model_class.__name__.lower() + "s"
            prefix = f"/api/{name}"
        
        from fastapi import HTTPException
        from ..data.database import db
        
        # GET all
        async def read_all():
            return db.find_all(model_class)
        self.add_api(prefix, read_all, method="GET")
        
        # GET one
        async def read_one(id: int):
            item = db.find_by_id(model_class, id)
            if not item:
                raise HTTPException(status_code=404, detail="Not found")
            return item
        self.add_api(f"{prefix}/:id", read_one, method="GET")
        
        # POST
        async def create(item: model_class):
            db.save(item)
            return item
        self.add_api(prefix, create, method="POST")
        
        # DELETE
        async def delete(id: int):
            item = db.find_by_id(model_class, id)
            if not item:
                raise HTTPException(status_code=404, detail="Not found")
            db.delete(item)
            return {"deleted": id}
        self.add_api(f"{prefix}/:id", delete, method="DELETE")
        
        print(f"✨ CRUD API generated at {prefix}")
        return self


# Backward compatibility
def auto_discover_pages(pages_dir: str = "pages") -> List[Tuple[str, Callable]]:
    """
    Backward compatible function.
    Use Router().discover() instead.
    """
    router = Router()
    router.discover(pages_dir)
    return [(r.path, r.handler) for r in router.routes.values()]
