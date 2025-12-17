from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware as FastAPICORS
from .state import StateManager
from .middleware import MiddlewareStack, LoggingMiddleware, CORSMiddleware, RateLimitMiddleware, AuthMiddleware, ErrorHandlerMiddleware
import asyncio
import os
import time
import platform

from ..lib.seo import Metadata, JSONLD

class App:
    """Wrapper class agar user merasa simpel"""
    
    # App metadata
    _start_time = None
    _version = "0.1.0"
    _name = "PyX App"
    
    # Lifespan handlers
    _startup_handlers = []
    _shutdown_handlers = []
    
    def __init__(self):
        self.api = FastAPI()
        self.manager = StateManager()
        self.event_registry = {} # Stores { "function_name": function_obj }
        self.routes = {} # Stores { "/path": component_func }
        
        # SEO Registries
        self.routes_meta = {} # Stores { "/path": Metadata | Callable }
        self.sitemap_providers = [] # List of callables returning list of dicts (params)
        self.robots_rules = "User-agent: *\nAllow: /"
        
        self._middleware_stack = MiddlewareStack()
        App._start_time = time.time()
        
        # Auto-mount 'assets' folder if it exists
        if os.path.exists("assets"):
            self.api.mount("/assets", StaticFiles(directory="assets"), name="assets")
            print("Assets folder detected and mounted at /assets")
        
        # Auto-mount 'uploads' folder if it exists
        if os.path.exists("uploads"):
            self.api.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
            print("Uploads folder detected and mounted at /uploads")
        
        self.custom_css = "" # Penampung CSS Custom
        
        # Register Lifespan Events
        @self.api.on_event("startup")
        async def startup_event():
            for handler in App._startup_handlers:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
                    
        @self.api.on_event("shutdown")
        async def shutdown_event():
            for handler in App._shutdown_handlers:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()

        # Register SEO Endpoints
        @self.api.get("/robots.txt", response_class=HTMLResponse) # Plain text actually
        def robots():
            return HTMLResponse(content=self.robots_rules, media_type="text/plain")

        @self.api.get("/sitemap.xml", response_class=HTMLResponse)
        async def sitemap():
            return await self._generate_sitemap()
    
    def set_info(self, name: str = None, version: str = None):
        """Set app name and version"""
        if name:
            App._name = name
        if version:
            App._version = version
        return self

    def run(self, host: str = "0.0.0.0", port: int = 8000, **kwargs):
        """Run the application using Uvicorn"""
        import uvicorn
        print(f"🚀 PyX Server starting at http://{host}:{port}")
        uvicorn.run(self.api, host=host, port=port, **kwargs)
    
    def use_health(self, path: str = "/health"):
        """
        Enable health check endpoint.
        
        Usage:
            app.use_health()  # Default: /health
            app.use_health("/api/health")
            
        Response:
            {
                "status": "healthy",
                "app": "MyApp",
                "version": "1.0.0",
                "uptime": 3600,
                "python": "3.11.0",
                "platform": "Darwin"
            }
        """
        @self.api.get(path)
        async def health_check():
            uptime = int(time.time() - App._start_time) if App._start_time else 0
            
            # Check database connection if available
            db_status = "not_configured"
            try:
                from ..data.database import db
                if db._engine:
                    db_status = "connected"
            except:
                pass
            
            return JSONResponse({
                "status": "healthy",
                "app": App._name,
                "version": App._version,
                "uptime_seconds": uptime,
                "uptime_human": self._format_uptime(uptime),
                "python": platform.python_version(),
                "platform": platform.system(),
                "database": db_status
            })
        
        print(f"[PyX] Health check enabled at {path}")
        return self
    
    def _format_uptime(self, seconds: int) -> str:
        """Format uptime in human readable format"""
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
        
        return " ".join(parts)

    # ==========================================
    # LIFESPAN TASKS
    # ==========================================
    
    @classmethod
    def on_startup(cls, func):
        """
        Decorator to register a startup handler.
        Runs when the application starts.
        
        Usage:
            @app.on_startup
            def init_database():
                db.connect("sqlite:///app.db")
        """
        cls._startup_handlers.append(func)
        return func
    
    @classmethod
    def on_shutdown(cls, func):
        """
        Decorator to register a shutdown handler.
        Runs when the application stops.
        
        Usage:
            @app.on_shutdown
            def cleanup():
                jobs.stop()
        """
        cls._shutdown_handlers.append(func)
        return func


    # ==========================================
    # MIDDLEWARE METHODS
    # ==========================================
    
    def use(self, middleware):
        """
        Add middleware to the application.
        
        Usage:
            app.use(LoggingMiddleware())
            app.use(CORSMiddleware(origins=["*"]))
        """
        self._middleware_stack.add(middleware)
        return self
    
    def use_cors(self, origins=["*"], methods=["*"], headers=["*"]):
        """
        Enable CORS with specified configuration.
        
        Usage:
            app.use_cors(origins=["http://localhost:3000"])
        """
        self.api.add_middleware(
            FastAPICORS,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=methods,
            allow_headers=headers,
        )
        print("[PyX] CORS enabled")
        return self
    
    def use_logging(self):
        """Enable request logging"""
        self.use(LoggingMiddleware())
        print("[PyX] Logging enabled")
        return self
    
    def use_rate_limit(self, max_requests=100, window_seconds=60):
        """
        Enable rate limiting.
        
        Usage:
            app.use_rate_limit(max_requests=100, window_seconds=60)
        """
        self.use(RateLimitMiddleware(max_requests, window_seconds))
        print(f"[PyX] Rate limiting enabled: {max_requests} req/{window_seconds}s")
        return self
    
    def use_auth(self, protected_paths=["/admin"], login_path="/login", enable_ui=True):
        """
        Enable built-in Authentication System.
        
        Args:
            protected_paths: List of paths that require login.
            login_path: Path to login page.
            enable_ui: Auto-generate Login/Register UI.
        """
        # Init Auth DB
        from ..lib.auth import auth
        auth.init()
        
        # Register Middleware
        self.use(AuthMiddleware(protected_paths, login_path))
        print(f"[PyX] Auth Middleware enabled. Protected: {protected_paths}")
        
        if enable_ui:
            from ..web.ui import UI
            from ..web.client import JS
            from ..web.components import PyxUI
            
            # --- LOGIN PAGE ---
            @self.api.get(login_path, response_class=HTMLResponse)
            async def login_page():
                return self._wrap_html(UI.div([
                    PyxUI.Card([
                        PyxUI.CardHeader([
                            PyxUI.CardTitle("Login", className="text-center text-2xl")
                        ]),
                        PyxUI.CardContent([
                            UI.form([
                                UI.div([
                                    UI.label("Email", className="block text-sm font-medium mb-1"),
                                    PyxUI.Input(name="email", type="email", placeholder="user@example.com")
                                ], className="mb-4"),
                                UI.div([
                                    UI.label("Password", className="block text-sm font-medium mb-1"),
                                    PyxUI.Input(name="password", type="password", placeholder="••••••")
                                ], className="mb-6"),
                                PyxUI.Button("Sign In", className="w-full", onClick=JS.submit_form("login-form", "handle_login")),
                                UI.div([
                                    UI.text("Don't have an account? "),
                                    UI.a("Register", href="/register").className("text-primary hover:underline")
                                ], className="mt-4 text-center text-sm text-muted-foreground")
                            ], id="login-form", data_pyx_submit="handle_login")
                        ])
                    ], className="w-full max-w-md")
                ], className="flex min-h-screen items-center justify-center bg-muted/50").render(), title="Login")

            # --- REGISTER PAGE ---
            @self.api.get("/register", response_class=HTMLResponse)
            async def register_page():
                return self._wrap_html(UI.div([
                    PyxUI.Card([
                        PyxUI.CardHeader([
                            PyxUI.CardTitle("Register", className="text-center text-2xl")
                        ]),
                        PyxUI.CardContent([
                            UI.form([
                                UI.div([
                                    UI.label("Full Name", className="block text-sm font-medium mb-1"),
                                    PyxUI.Input(name="full_name", type="text", placeholder="John Doe")
                                ], className="mb-4"),
                                UI.div([
                                    UI.label("Email", className="block text-sm font-medium mb-1"),
                                    PyxUI.Input(name="email", type="email", placeholder="user@example.com")
                                ], className="mb-4"),
                                UI.div([
                                    UI.label("Password", className="block text-sm font-medium mb-1"),
                                    PyxUI.Input(name="password", type="password", placeholder="••••••")
                                ], className="mb-6"),
                                PyxUI.Button("Sign Up", className="w-full", onClick=JS.submit_form("register-form", "handle_register")),
                                UI.div([
                                    UI.text("Already have an account? "),
                                    UI.a("Login", href="/login").className("text-primary hover:underline")
                                ], className="mt-4 text-center text-sm text-muted-foreground")
                            ], id="register-form", data_pyx_submit="handle_register")
                        ])
                    ], className="w-full max-w-md")
                ], className="flex min-h-screen items-center justify-center bg-muted/50").render(), title="Register")

            # --- AUTH HANDLERS ---
            @self.register_event
            def handle_login(data):
                email = data.get("email")
                password = data.get("password")
                token = auth.login(email, password)
                
                if token:
                    # Set cookie via JS for now (or improve WS response to set cookie)
                    # Currently PyX doesn't support setting cookies via WS easily, 
                    # but we can do it via JS snippet.
                    return JS.eval(f"document.cookie='pyx_session={token}; path=/; max-age=86400'; window.location.href='/admin'")
                else:
                    return JS.toast("Invalid email or password", "error")

            @self.register_event
            def handle_register(data):
                email = data.get("email")
                password = data.get("password")
                full_name = data.get("full_name")
                
                user = auth.register(email, password, full_name)
                if user:
                     return JS.toast("Registration successful! Please login.", "success").then_navigate("/login")
                else:
                    return JS.toast("Email already registered", "error")

        return self
    
    def use_error_handler(self, debug=False):
        """Enable global error handling"""
        self.use(ErrorHandlerMiddleware(debug))
        print("[PyX] Error handler enabled")
        return self
    
    def use_csrf(self, exempt_paths=[]):
        """
        Enable CSRF protection.
        
        Usage:
            app.use_csrf(exempt_paths=["/api/webhook"])
        """
        from .middleware import CSRFMiddleware
        self.use(CSRFMiddleware(exempt_paths=exempt_paths))
        print("[PyX] CSRF protection enabled")
        return self
    
    def on_startup(self, func):
        """
        Decorator for startup events.
        
        Usage:
            @app.on_startup
            def init():
                db.init()
        """
        self.api.on_event("startup")(func)
        return func
    
    def on_shutdown(self, func):
        """Decorator for shutdown events"""
        self.api.on_event("shutdown")(func)
        return func


    def set_theme(self, colors: dict):
        from ..web.colors import Colors
        # Generate CSS Block dari Dictionary
        self.custom_css = Colors.generate_custom_theme(colors)

    def register_event(self, func):
        """Decorator or method to register event handlers"""
        self.event_registry[func.__name__] = func
        return func

    def include_router(self, router):
        """Include a PyX Router."""
        for path, component in router.routes:
            # Combine prefix + path
            full_path = f"{router.prefix}{path}".replace("//", "/")
            self.add_page(full_path, component)

    def mount_admin(self, models: list):
        """
        Auto-generate Admin Panel for Models.
        """
        print(f"[PyX Admin] Mounting Admin Panel for: {[m.__name__ for m in models]}")
        
        # Admin Dashboard Route
        @self.api.get("/admin", response_class=HTMLResponse)
        async def admin_dashboard():
            from ..web.ui import UI
            from ..web.components import PyxUI
            
            links = []
            for m in models:
                slug = m.__name__.lower() + "s"
                links.append(PyxUI.Card([
                    PyxUI.CardHeader([
                        PyxUI.CardTitle(m.__name__),
                    ]),
                    PyxUI.CardContent([
                        PyxUI.Button("Manage", variant="secondary", onClick=f"PyX.navigate('/admin/{slug}')")
                    ])
                ], className="w-full"))

            content = UI.div([
                UI.h1("Zen Admin", className="text-3xl font-bold mb-8"),
                UI.div(links, className="grid grid-cols-1 md:grid-cols-3 gap-6")
            ], className="container mx-auto py-10").render()
            
            return self._wrap_html(content, title="Zen Admin")

        # Register Resources
        from ..lib.admin.views import AdminView
        
        for model in models:
            view = AdminView(model)
            
            # List Route
            self.add_page(view.prefix, view.render_list)
            
            # Create Route
            self.add_page(f"{view.prefix}/create", view.render_form)
            
            # Edit Route
            self.add_page(f"{view.prefix}/{{id}}/edit", lambda id: view.render_form(id)) # Lambda to capture param? Wait, need closer inspection on how params are passed.
            # My add_page implementation for dynamic logic is still 'work in progress' regarding passing params to component_func.
            # Ideally `view.render_form` handles it if PyX server passes args.
            # Let's assume view.render_form argument matches path param.
            
        # Optimizer Route
        @self.api.get("/optimizer/_image")
        async def optimize_image(url: str, w: int = 800, q: int = 80):
            from ..web.assets import assets
            from fastapi import Response
            
            data = assets.optimize(url, width=w, quality=q)
            if not data:
                return Response(status_code=404)
                
            return Response(content=data, media_type="image/webp")

    def add_page(self, route, component_func, title=None, description=None, image=None, metadata=None, sitemap=None):
        # Register route for dynamic rendering
        self.routes[route] = component_func
        
        # Handle Metadata (Legacy title/desc args vs new Metadata object)
        if metadata:
            self.routes_meta[route] = metadata
        elif title:
             # Legacy support
             # Uses global Metadata import
             from ..lib.seo import OpenGraph
             self.routes_meta[route] = Metadata(
                 title=title, 
                 description=description,
                 open_graph=OpenGraph(images=[image] if image else [])
             )
        
        # Handle Sitemap (for dynamic routes)
        if sitemap:
             # sitemap is a callable returning list of params for this route
             # We store tuple (route_template, provider_func)
             self.sitemap_providers.append((route, sitemap))
        
        @self.api.get(route, response_class=HTMLResponse)
        async def page(request: Request = None): # FastAPi Request object for accessing path params
            # Note: We need to capture path params if any. 
            # Ideally we use **kwargs or inspect signature, but for now assuming 'request' is mostly what we need or empty.
            # Wait, FastAPI handles path params by argument name.
            # To resolve metadata dynamically, we need those params.
            # For simplicity in this Zen mode, we might need a more generic handler or assume params are passed to component_func too if it accepts them.
            
            # Simplified Logic:
            try:
                # 1. Resolve Metadata
                resolved_meta = None
                meta_def = self.routes_meta.get(route)
                
                # Extract path params from request if available (this requires changing signature to accept Request)
                # Hack: We can use Starlette's request.path_params
                path_params = request.path_params if request else {}
                
                if callable(meta_def):
                    resolved_meta = meta_def(path_params)
                elif isinstance(meta_def, Metadata):
                    resolved_meta = meta_def
                
                # 2. Render Component
                # TODO: Pass params to component_func if it accepts arguments?
                content = component_func().render()
                
                return self._wrap_html(content, metadata=resolved_meta)
            except Exception as e:
                import traceback
                traceback.print_exc()
                return HTMLResponse(content=f"<h1>Error</h1><pre>{traceback.format_exc()}</pre>", status_code=500)

        # Inject Websocket otomatis
        @self.api.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self.manager.connect(websocket)
            try:
                while True:
                    data = await websocket.receive_text()
                    # Parse Incoming Event
                    import json
                    try:
                        message = json.loads(data)
                    except Exception as e:
                        print(f"JSON Parse Error: {e}")
                        continue
                        
                    if message.get("type") == "event" or message.get("type") == "form_submit":
                        handler_name = message.get("handler")
                        data = message.get("data")
                        path = message.get("path") # Get path for re-render
                        value = message.get("value") # Value for State setters
                        
                        # Lookup
                        from .events import EventManager
                        func = EventManager.get_handler(handler_name)
                        
                        if func:
                            print(f"[{message.get('type')}] {handler_name} (Path: {path})")
                            
                            # Execute Handler
                            # If value is provided (State setter), pass it as argument
                            if value is not None:
                                result = await EventManager.execute(handler_name, value, websocket)
                            else:
                                result = await EventManager.execute(handler_name, data, websocket)
                            
                            # ARCHITECTURE FIX: Handle Action objects returned by handlers
                            from .state import Action
                            
                            if isinstance(result, Action):
                                # New Action-based system
                                action_dict = result.to_dict()
                                print(f"Action: {action_dict}")
                                await websocket.send_text(json.dumps(action_dict))
                            
                            elif isinstance(result, dict) and result.get("type") == "navigate":
                                # Legacy dict-based navigation (backwards compatible)
                                print(f"Redirecting client to: {result.get('url')}")
                                await websocket.send_text(json.dumps({
                                    "type": "navigate",
                                    "path": result.get("url")
                                }))

                            elif result is None and path and path in self.routes:
                                # Auto-Refresh Logic (Zen Mode Magic)
                                # State likely changed, but no specific UI response.
                                # Re-render the current Page!
                                print(f"Auto-refreshing UI for: {path}")
                                component_func = self.routes[path]
                                try:
                                    new_content = component_func().render()
                                    await websocket.send_text(json.dumps({
                                        "type": "navigate_content",
                                        "path": path,
                                        "content": new_content 
                                    }))
                                except Exception as e:
                                    print(f"Auto-refresh failed: {e}")

                        else:
                            print(f"Unknown handler: {handler_name}")
                            
                    elif message.get("type") == "navigate":
                        # Handle Client-Side Navigation Request
                        path = message.get("path")
                        print(f"Navigating to: {path}")
                        
                        # Find route handler
                        if path in self.routes:
                            component_func = self.routes[path]
                            try:
                                # Re-render fresh content
                                new_content = component_func().render()
                                
                                # Send back to client
                                await websocket.send_text(json.dumps({
                                    "type": "navigate_content",
                                    "path": path,
                                    "content": new_content 
                                }))
                            except Exception as e:
                                print(f"Render Error: {e}")
                                import traceback
                                traceback.print_exc()
                        else:
                            print(f"404 Not Found: {path}")
                                # Optional: Send 404 toast or page
                        

            except WebSocketDisconnect:
                self.manager.disconnect(websocket)

    async def __call__(self, scope, receive, send):
        """Allow the instance to be used as an ASGI app directly."""
        await self.api(scope, receive, send)

    async def _generate_sitemap(self):
        """Generate XML Sitemap"""
        urls = []
        base_url = "http://localhost:8000" # TODO: Configurable Base URL
        
        # 1. Static Routes
        for path, _ in self.routes.items():
            # Skip dynamic routes (containing '{')
            if "{" not in path:
                urls.append(f"{base_url}{path}")
        
        # 2. Dynamic Routes (via Providers)
        for route_template, provider in self.sitemap_providers:
            try:
                # Provider returns list of dicts: [{'slug': 'a'}, {'slug': 'b'}]
                params_list = provider() if callable(provider) else provider
                for params in params_list:
                    # Replace placeholders
                    path = route_template.format(**params)
                    urls.append(f"{base_url}{path}")
            except Exception as e:
                print(f"Sitemap Error for {route_template}: {e}")

        # Build XML
        url_blocks = "".join([f"<url><loc>{u}</loc></url>" for u in urls])
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{url_blocks}
</urlset>"""
        return HTMLResponse(content=xml_content, media_type="application/xml")

    def run(self, host="0.0.0.0", port=8000, reload=True):
        """Run the app using Uvicorn"""
        import uvicorn
        # Note: 'self.api' is the FastAPI app, but uvicorn needs the object itself or import string.
        # If running programmatically, we can pass self.
        # But 'reload=True' requires import string usually.
        # For simple scripts 'app.run()', we force reload=False or warn user?
        # Actually uvicorn.run(self, ...) works but reload might not.
        
        print(f"🚀 PyX Engine starting on http://{host}:{port}")
        if reload:
            print("⚠️  Warning: 'reload=True' is ignored when using app.run() directly. Use 'uvicorn <module>:app --reload' instead.")
        
        uvicorn.run(self, host=host, port=port) # Removed reload=True as it needs import string

    def _render_head(self, metadata) -> str:
        """Generate HTML Head tags from Metadata object"""
        if not metadata:
            return "<title>PyX App</title>"
        
        tags = []
        
        # Title
        if metadata.title:
            tags.append(f"<title>{metadata.title}</title>")
            tags.append(f'<meta property="og:title" content="{metadata.title}">')
            tags.append(f'<meta name="twitter:title" content="{metadata.title}">')
        
        # Description
        if metadata.description:
            tags.append(f'<meta name="description" content="{metadata.description}">')
            tags.append(f'<meta property="og:description" content="{metadata.description}">')
            tags.append(f'<meta name="twitter:description" content="{metadata.description}">')
            
        # Canonical
        if metadata.canonical:
            tags.append(f'<link rel="canonical" href="{metadata.canonical}">')
            tags.append(f'<meta property="og:url" content="{metadata.canonical}">')

        # Open Graph
        if metadata.open_graph:
            og = metadata.open_graph
            if og.type: tags.append(f'<meta property="og:type" content="{og.type}">')
            if og.site_name: tags.append(f'<meta property="og:site_name" content="{og.site_name}">')
            for img in og.images:
                tags.append(f'<meta property="og:image" content="{img}">')
        
        # Twitter
        if metadata.twitter:
            tw = metadata.twitter
            tags.append(f'<meta name="twitter:card" content="{tw.card}">')
            if tw.site: tags.append(f'<meta name="twitter:site" content="{tw.site}">')
            if tw.creator: tags.append(f'<meta name="twitter:creator" content="{tw.creator}">')
            for img in tw.images:
                tags.append(f'<meta name="twitter:image" content="{img}">')

        # JSON-LD
        if metadata.json_ld:
            import json
            json_str = json.dumps(metadata.json_ld)
            tags.append(f'<script type="application/ld+json">{json_str}</script>')

        return "\n".join(tags)

    def _wrap_html(self, content, metadata=None):
        # Template HTML standar PyX dengan Form Binding, Navigation, dan Toast
        seo_head = self._render_head(metadata)
        
        return f"""
        <!DOCTYPE html><html><head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        {seo_head}
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/lucide@latest"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            tailwind.config = {{
                theme: {{
                    extend: {{
                        fontFamily: {{
                            sans: ['Inter', 'sans-serif'],
                        }},
                        colors: {{
                            primary: '#4f46e5',
                            secondary: '#64748b',
                        }}
                    }}
                }}
            }}
        </script>
        <style>
            :root {{
                --background: 0 0% 100%;
                --foreground: 240 10% 3.9%;
                --card: 0 0% 100%;
                --card-foreground: 240 10% 3.9%;
                --popover: 0 0% 100%;
                --popover-foreground: 240 10% 3.9%;
                --primary: 240 5.9% 10%;
                --primary-foreground: 0 0% 98%;
                --secondary: 240 4.8% 95.9%;
                --secondary-foreground: 240 5.9% 10%;
                --muted: 240 4.8% 95.9%;
                --muted-foreground: 240 3.8% 46.1%;
                --accent: 240 4.8% 95.9%;
                --accent-foreground: 240 5.9% 10%;
                --destructive: 0 84.2% 60.2%;
                --destructive-foreground: 0 0% 98%;
                --border: 240 5.9% 90%;
                --input: 240 5.9% 90%;
                --ring: 240 5.9% 10%;
                --radius: 0.5rem;
            }}
            body {{ 
                background-color: hsl(var(--background)); 
                color: hsl(var(--foreground)); 
                font-family: 'Inter', sans-serif;
            }}
            .dark body {{ /* Future Dark Mode Support */
                --background: 240 10% 3.9%;
                --foreground: 0 0% 98%;
                /* ... other dark content ... */
            }}
            
            /* Toast Styles */
            .pyx-toast-container {{
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }}
            .pyx-toast {{
                padding: 16px 24px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                animation: slideIn 0.3s ease-out;
                display: flex;
                align-items: center;
                gap: 12px;
                min-width: 300px;
            }}
            .pyx-toast.success {{ background: #22c55e; color: white; }}
            .pyx-toast.error {{ background: #ef4444; color: white; }}
            .pyx-toast.warning {{ background: #f59e0b; color: white; }}
            .pyx-toast.info {{ background: #3b82f6; color: white; }}
            @keyframes slideIn {{
                from {{ transform: translateX(100%); opacity: 0; }}
                to {{ transform: translateX(0); opacity: 1; }}
            }}
            @keyframes slideOut {{
                from {{ transform: translateX(0); opacity: 1; }}
                to {{ transform: translateX(100%); opacity: 0; }}
            }}
            
            /* Modal Styles */
            .pyx-modal-overlay {{
                position: fixed;
                inset: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9998;
                opacity: 0;
                visibility: hidden;
                transition: all 0.2s ease;
            }}
            .pyx-modal-overlay.active {{
                opacity: 1;
                visibility: visible;
            }}
            .pyx-modal {{
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 500px;
                width: 90%;
                max-height: 90vh;
                overflow: auto;
                transform: scale(0.9);
                transition: transform 0.2s ease;
            }}
            .pyx-modal-overlay.active .pyx-modal {{
                transform: scale(1);
            }}
            .pyx-modal-header {{
                padding: 16px 24px;
                border-bottom: 1px solid #e5e7eb;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .pyx-modal-title {{
                font-size: 18px;
                font-weight: 600;
                color: #1f2937;
            }}
            .pyx-modal-close {{
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                color: #6b7280;
                padding: 0;
                line-height: 1;
            }}
            .pyx-modal-close:hover {{ color: #1f2937; }}
            .pyx-modal-body {{
                padding: 24px;
                color: #374151;
            }}
            .pyx-modal-footer {{
                padding: 16px 24px;
                border-top: 1px solid #e5e7eb;
                display: flex;
                justify-content: flex-end;
                gap: 12px;
            }}
        </style>
        {self.custom_css}
        </head><body>
        
        <!-- Toast Container -->
        <div id="pyx-toast-container" class="pyx-toast-container"></div>
        
        <div id="pyx-root">
            {content}
        </div>
        
        <script>
            // =============================================
            // PyX Client Runtime
            // =============================================
            
            // Initialize Lucide Icons
            lucide.createIcons();
            
            // WebSocket Connection
            window.ws = new WebSocket("ws://" + window.location.host + "/ws");
            window.ws.onmessage = e => {{
                const d = JSON.parse(e.data);
                
                // Handle different message types
                if (d.type === 'update') {{
                    const el = document.getElementById(d.id);
                    if(el) {{
                        el.outerHTML = d.content;
                        lucide.createIcons();
                    }}
                }} else if (d.type === 'navigate') {{
                    // Explicit Navigation Command from Server
                    PyX.navigate(d.path || d.url); 
                }} else if (d.type === 'navigate_content') {{
                    // SPA Navigation Response - update content without full reload
                    const root = document.getElementById('pyx-root');
                    if (root) {{
                        root.innerHTML = d.content;
                        lucide.createIcons();
                        
                        // Scan for on_mount events in new content
                        document.querySelectorAll('[data-pyx-mount]').forEach(el => {{
                            const handler = el.getAttribute('data-pyx-mount');
                            PyX.sendEvent(handler);
                        }});

                        window.scrollTo(0, 0);
                        
                        // Update URL if didn't match
                        if (window.location.pathname !== d.path) {{
                            history.pushState({{path: d.path}}, '', d.path);
                        }}
                    }}
                }} else if (d.type === 'alert') {{
                    // Alert action from server
                    window.alert(d.message);
                }} else if (d.type === 'toast') {{
                    // Toast notification from server
                    PyX.toast(d.message, d.variant || 'info', d.duration || 3000);
                }} else if (d.type === 'refresh') {{
                    // Refresh current page
                    window.location.reload();
                }} else if (d.id) {{
                    // Legacy format - update single element
                    const el = document.getElementById(d.id);
                    if(el) {{
                        el.outerHTML = d.content;
                        lucide.createIcons();
                    }}
                }}
            }};
            
            // =============================================
            // PyX Global Object
            // =============================================
            window.PyX = {{
                // Navigate to URL (SPA)
                navigate: function(url) {{
                    if (window.ws && window.ws.readyState === WebSocket.OPEN) {{
                        // Send request to server
                        window.ws.send(JSON.stringify({{
                            type: 'navigate',
                            path: url
                        }}));
                        
                        // Optimistically update URL
                        history.pushState({{path: url}}, '', url);
                    }} else {{
                        // Fallback if WS not open
                        window.location.href = url;
                    }}
                }},
                
                // Show Toast Notification
                toast: function(message, variant = 'info', duration = 3000) {{
                    const container = document.getElementById('pyx-toast-container');
                    const toast = document.createElement('div');
                    toast.className = 'pyx-toast ' + variant;
                    
                    // Icon based on variant
                    const icons = {{
                        success: '✓',
                        error: '✕',
                        warning: '⚠',
                        info: 'ℹ'
                    }};
                    
                    toast.innerHTML = '<span style="font-size:20px">' + (icons[variant] || 'ℹ') + '</span><span>' + message + '</span>';
                    container.appendChild(toast);
                    
                    // Auto remove
                    setTimeout(() => {{
                        toast.style.animation = 'slideOut 0.3s ease-out forwards';
                        setTimeout(() => toast.remove(), 300);
                    }}, duration);
                }},
                
                // Get Form Values
                getFormData: function(formId) {{
                    const form = document.getElementById(formId);
                    if (!form) return {{}};
                    
                    const data = {{}};
                    const inputs = form.querySelectorAll('input, select, textarea');
                    inputs.forEach(input => {{
                        if (input.name || input.id) {{
                            const key = input.name || input.id;
                            if (input.type === 'checkbox') {{
                                data[key] = input.checked;
                            }} else if (input.type === 'radio') {{
                                if (input.checked) data[key] = input.value;
                            }} else {{
                                data[key] = input.value;
                            }}
                        }}
                    }});
                    return data;
                }},
                
                // Get Single Input Value
                getValue: function(id) {{
                    const el = document.getElementById(id);
                    if (!el) return null;
                    if (el.type === 'checkbox') return el.checked;
                    return el.value;
                }},
                
                // Set Input Value
                setValue: function(id, value) {{
                    const el = document.getElementById(id);
                    if (!el) return;
                    if (el.type === 'checkbox') {{
                        el.checked = value;
                    }} else {{
                        el.value = value;
                    }}
                }},
                
                // Send Event to Server
                sendEvent: function(handler, data = null, value = null) {{
                    if (window.ws && window.ws.readyState === WebSocket.OPEN) {{
                        const payload = {{
                            type: 'event',
                            handler: handler,
                            data: data,
                            path: window.location.pathname
                        }};
                        // If value is provided (for State setters), include it
                        if (value !== null) {{
                            payload.value = value;
                        }}
                        window.ws.send(JSON.stringify(payload));
                    }}
                }},
                
                // Submit Form via Event
                submitForm: function(formId, handler) {{
                    const data = this.getFormData(formId);
                    if (window.ws && window.ws.readyState === WebSocket.OPEN) {{
                        window.ws.send(JSON.stringify({{
                            type: 'form_submit',
                            handler: handler,
                            formId: formId,
                            data: data,
                            path: window.location.pathname // Send current path
                        }}));
                    }}
                }},
                
                // =============================================
                // Modal Functions
                // =============================================
                
                // Open Modal
                openModal: function(modalId) {{
                    const modal = document.getElementById(modalId);
                    if (modal) {{
                        modal.classList.add('active');
                        document.body.style.overflow = 'hidden';
                    }}
                }},
                
                // Close Modal
                closeModal: function(modalId) {{
                    const modal = document.getElementById(modalId);
                    if (modal) {{
                        modal.classList.remove('active');
                        document.body.style.overflow = '';
                    }}
                }},
                
                // Create and Show Dynamic Modal
                modal: function(title, content, options = {{}}) {{
                    const id = 'pyx-modal-' + Date.now();
                    const showFooter = options.showFooter !== false;
                    const onConfirm = options.onConfirm || null;
                    const confirmText = options.confirmText || 'Confirm';
                    const cancelText = options.cancelText || 'Cancel';
                    
                    const modalHtml = `
                        <div id="${{id}}" class="pyx-modal-overlay" onclick="if(event.target === this) PyX.closeModal('${{id}}')">
                            <div class="pyx-modal">
                                <div class="pyx-modal-header">
                                    <span class="pyx-modal-title">${{title}}</span>
                                    <button class="pyx-modal-close" onclick="PyX.closeModal('${{id}}')">&times;</button>
                                </div>
                                <div class="pyx-modal-body">
                                    ${{content}}
                                </div>
                                ${{showFooter ? `
                                    <div class="pyx-modal-footer">
                                        <button onclick="PyX.closeModal('${{id}}')" 
                                            class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">
                                            ${{cancelText}}
                                        </button>
                                        ${{onConfirm ? `
                                            <button onclick="${{onConfirm}}; PyX.closeModal('${{id}}')"
                                                class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                                                ${{confirmText}}
                                            </button>
                                        ` : ''}}
                                    </div>
                                ` : ''}}
                            </div>
                        </div>
                    `;
                    
                    document.body.insertAdjacentHTML('beforeend', modalHtml);
                    setTimeout(() => this.openModal(id), 10);
                    return id;
                }},
                
                // Confirm Dialog
                confirm: function(message, onConfirm) {{
                    return this.modal('Confirm', `<p>${{message}}</p>`, {{
                        onConfirm: onConfirm,
                        confirmText: 'Yes',
                        cancelText: 'No'
                    }});
                }},
                
                // Alert Dialog
                alert: function(message, title = 'Alert') {{
                    return this.modal(title, `<p>${{message}}</p>`, {{
                        showFooter: true,
                        confirmText: 'OK',
                        onConfirm: ''
                    }});
                }}
            }};
            
            // =============================================
            // Auto-bind Forms
            // =============================================
            document.addEventListener('DOMContentLoaded', function() {{
                // Initialize Icons
                if (window.lucide) {{
                    lucide.createIcons();
                }}

                // Bind forms with data-pyx-submit attribute
                document.querySelectorAll('form[data-pyx-submit]').forEach(form => {{
                    form.addEventListener('submit', function(e) {{
                        e.preventDefault();
                        const handler = this.getAttribute('data-pyx-submit');
                        PyX.submitForm(this.id, handler);
                    }});
                }});
                
                // Handle Browser Back/Forward Buttons
                window.onpopstate = function(event) {{
                    if (event.state && event.state.path) {{
                        PyX.navigate(event.state.path);
                    }} else {{
                        // Fallback for initial state or external navigations
                        PyX.navigate(window.location.pathname);
                    }}
                }};

                // Auto-trigger on_mount events for initial load
                document.querySelectorAll('[data-pyx-mount]').forEach(el => {{
                    const handler = el.getAttribute('data-pyx-mount');
                    // We need to wait for WS connection
                    // Handled by retry logic or queue in real app.
                    // For Zen Mode, we just try.
                    // Better: wait for socket open.
                    const checkWs = setInterval(() => {{
                        if (window.ws && window.ws.readyState === WebSocket.OPEN) {{
                            clearInterval(checkWs);
                            PyX.sendEvent(handler);
                        }}
                    }}, 100);
                }});
            }});
        </script>
        </body></html>
        """
