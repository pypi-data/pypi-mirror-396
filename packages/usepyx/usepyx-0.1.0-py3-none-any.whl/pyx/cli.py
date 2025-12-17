import typer
import uvicorn
import os
import sys
from pathlib import Path

app = typer.Typer(help="PyX Framework CLI")

# --- TEMPLATES ---

TEMPLATE_MAIN = """import pyx
from pyx import UI

# Import Modules
from modules.home import home_view

app = pyx.App()

# Register Routes
app.add_page("/", home_view)

if __name__ == "__main__":
    app.run()
"""

TEMPLATE_STATE = """from pyx import State

class {name_cap}State(State):
    \"\"\"
    Model (State): Holds the reactive data for {name} module.
    \"\"\"
    # Example state variable
    # count: int = 0
    pass
"""

TEMPLATE_CONTROLLER = """from .state import {name_cap}State
import pyx

class {name_cap}Controller:
    \"\"\"
    Controller: Logic handlers for {name} module.
    \"\"\"
    
    @staticmethod
    def example_action():
        print("Action triggered in {name} module")
        # {name_cap}State.count += 1
"""

TEMPLATE_VIEW = '''from pyx import UI, ui, Card

def {name}_view():
    """
    View: Onboarding / Welcome Page (Ultra Zen Mode).
    """
    
    # --- Helpers ---
    def feature_item(icon, title, desc, link_text):
        """Reusable feature item layout"""
        return ui.div(
            ui.div(
                ui.i(data_lucide=icon).w(6).h(6).text("red-500")
            ).w(12).h(12).rounded("lg").bg("red-50").flex().items("center").justify("center").shrink_0(),
            
            ui.div(
                ui.h3(title).text("xl").font("bold").text("gray-900").mb(2),
                ui.p(desc).text("gray-600").leading("relaxed").mb(3).text("sm"),
                ui.a(
                    link_text,
                    ui.i(data_lucide="arrow-right").w(4).h(4).ml(2)
                ).inline_flex().items("center").text("red-500").font("semibold").text("sm").group_hover("translate-x-1").transition("transform").cursor("pointer")
            ).flex_1()
        ).flex().items("start").gap(5)

    # --- Components ---
    
    # 1. Background Layer
    bg_layer = ui.div(
        ui.div().absolute().top(0).left(0).w("700px").h("700px").style(background="linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(244, 63, 94, 0.1), transparent)").style(border_radius="9999px", filter="blur(60px)", transform="translate(-50%, -50%)").z(0),
        ui.div().absolute().bottom(0).right(0).w("500px").h("500px").style(background="linear-gradient(315deg, rgba(249, 115, 22, 0.15), rgba(239, 68, 68, 0.08), transparent)").style(border_radius="9999px", filter="blur(60px)", transform="translate(33%, 33%)").z(0)
    ).absolute().top(0).left(0).w_full().h_full().z(0)

    # 2. Documentation Card content
    mockup_header = ui.div(
        ui.div(
            ui.div().w(2.5).h(2.5).rounded("full").bg("red-400"),
            ui.div().w(2.5).h(2.5).rounded("full").bg("yellow-400"),
            ui.div().w(2.5).h(2.5).rounded("full").bg("green-400"),
        ).flex().gap(1.5),
        ui.div("docs.pyx.framework").ml(3).flex_1().bg("white").rounded().px(3).py(1).text("xs").text("gray-400").border().border_color("gray-200")
    ).flex().items("center").gap(2).mb(3)

    browser_mockup = ui.div(
        mockup_header,
        ui.div().h(40).bg("gray-100").rounded().border().border_color("gray-200")
    ).mb(6).bg("gray-50").rounded("lg").p(5).border().border_color("gray-200")

    doc_content = ui.div(
        browser_mockup,
        ui.div(
            ui.i(data_lucide="book-open").w(6).h(6).text("red-500"),
        ).w(12).h(12).rounded("lg").bg("red-50").flex().items("center").justify("center").mb(5),
        
        ui.h2("Documentation").text("2xl").font("bold").text("gray-900").mb(3),
        ui.p("PyX has wonderful documentation covering every aspect of the framework. Whether you are a newcomer or have prior experience with PyX, we recommend reading our documentation from beginning to end.").text("gray-600").leading("relaxed").mb(5).text("sm"),
        
        ui.a(
            "Read Documentation",
            ui.i(data_lucide="arrow-right").w(4).h(4).ml(2),
        ).inline_flex().items("center").text("red-500").font("semibold").text("sm").hover("text-red-600").hover("gap-3").transition("all").cursor("pointer").no_underline()
    ).h_full().flex().flex_col()
    
    # Using Card() and chaining styles for Glassmorphism effect
    doc_card = Card(doc_content, padding="lg").bg("white/70").backdrop_blur("sm").cls("lg:row-span-2").group().hover("shadow-md").transition("shadow").duration(300)

    # 3. Feature Cards
    pyx_card = Card(
        feature_item("sparkles", "PyX Framework", "PyX empowers you to build modern, reactive web applications entirely in Python. Forget about complex JavaScript build tools.", "Learn More")
    ).bg("white/70").backdrop_blur("sm").group().hover("shadow-md").transition("shadow").duration(300)
    
    batt_card = Card(
        feature_item("layers", "Batteries Included", "PyX ships with everything you need: Authentication, Database ORM, Real-time WebSockets, Background Jobs, and more.", "Explore Modules")
    ).bg("white/70").backdrop_blur("sm").group().hover("shadow-md").transition("shadow").duration(300)
    
    ai_card = Card(
        feature_item("cpu", "AI & Cloud Native", "Built for the future with first-class support for AI LLM integration and unified Cloud Storage (S3/GCS). Deploy anywhere with our Rust-powered engine for maximum performance.", "Deploy AI")
    ).bg("white/70").backdrop_blur("sm").group().hover("shadow-md").transition("shadow").duration(300)
    
    footer = ui.div("PyX v0.1.0 (Python v3.11)").text_align("center").pb(8).text("xs").text("gray-500")

    # --- Assembly ---
    return ui.div(
        bg_layer,
        
        ui.div(
            ui.div(
                doc_card,
                ui.div(pyx_card, batt_card,ai_card).grid().cols(1).gap(6)
            ).grid().cols(1).lg("grid-cols-2").gap(6),
            
            ui.div().h(8),
            footer
        ).max_w("6xl").mx("auto").px(6).pb(6).relative().z(10).w_full()

    ).min_h("100vh").bg("white").relative().overflow("hidden").font("Inter").pt(40)
'''

TEMPLATE_INIT = """from .views import {name}_view
"""

# --- AUTH TEMPLATES ---

TEMPLATE_AUTH_MODEL = """from pyx import db
from datetime import datetime
from typing import Optional

class User(db.Model, table=True):
    id: Optional[int] = db.Column(primary_key=True)
    email: str = db.Column(unique=True, index=True)
    password_hash: str = db.Column()
    full_name: Optional[str] = db.Column(default=None)
    created_at: datetime = db.CreatedAt()
    updated_at: datetime = db.UpdatedAt()
    
    def __repr__(self):
        return f"<User {self.email}>"
"""

TEMPLATE_AUTH_STATE = """from pyx import State
from typing import Optional

class AuthState(State):
    user: Optional[object] = None
    error: Optional[str] = None
    is_login_view: bool = True  # Toggle between Login/Register
"""

TEMPLATE_AUTH_CONTROLLER = """from .state import AuthState
from .models import User
from pyx import security, db
import pyx

class AuthController:
    @staticmethod
    def toggle_view():
        AuthState.is_login_view = not AuthState.is_login_view
        AuthState.error = None

    @staticmethod
    def login(email: str, password: str):
        if not email or not password:
            AuthState.error = "Please fill in all fields"
            return

        user = db.query(User).where(email=email).first()
        if user and security.verify_password(password, user.password_hash):
            AuthState.user = user
            AuthState.error = None
            print(f"✅ User {user.email} logged in!")
            # In a real app, you might redirect here
            # pyx.navigate("/dashboard")
        else:
            AuthState.error = "Invalid email or password"

    @staticmethod
    def register(email: str, password: str, confirm_password: str):
        if not email or not password:
            AuthState.error = "Please fill in all fields"
            return

        if password != confirm_password:
            AuthState.error = "Passwords do not match"
            return

        # Check existing
        if db.query(User).where(email=email).first():
            AuthState.error = "Email already registered"
            return
            
        try:
            hashed = security.hash_password(password)
            new_user = User(email=email, password_hash=hashed)
            db.save(new_user)
            
            AuthState.user = new_user
            AuthState.error = None
            print(f"✅ User {email} registered!")
        except Exception as e:
            AuthState.error = f"Registration failed: {str(e)}"
    
    @staticmethod
    def logout():
        AuthState.user = None
"""

TEMPLATE_AUTH_VIEW = '''from pyx import ui, Card
from .state import AuthState
from .controller import AuthController

def auth_view():
    """
    View: Authentication Page (Login/Register)
    """
    
    # --- Components ---
    
    def input_field(label, type="text", placeholder="", bind_value=None):
        return ui.div(
            ui.label(label).block().text("sm").font("medium").text("gray-700").mb(1),
            ui.input(type=type, placeholder=placeholder).w_full().p(2).border().rounded("md").outline_none().focus("ring-2").focus("ring-red-500").focus("border-transparent")
            # In real usage, you would bind value here: .bind_value(bind_value)
            # For this demo, we assume the framework handles form submission binding automagically or via ID
        ).mb(4)

    # 1. Login Form
    login_form = ui.div(
        ui.h2("Welcome Back").text("2xl").font("bold").text_align("center").mb(6),
        
        # Error Banner
        ui.div(AuthState.error).bg("red-50").text("red-600").p(3).rounded("md").text("sm").mb(4) if AuthState.error else "",
        
        # Inputs (ID is used for argument mapping in controller)
        ui.input(type="email", placeholder="you@example.com").id("login_email").w_full().p(2).border().rounded("md").mb(3),
        ui.input(type="password", placeholder="••••••••").id("login_password").w_full().p(2).border().rounded("md").mb(6),
        
        # Action
        ui.button("Sign In").w_full().bg("red-500").text("white").p(2).rounded("md").font("medium").hover("bg-red-600").transition()
            .on_click(AuthController.login, args=["login_email.value", "login_password.value"]),
            
        ui.div(
            "Don't have an account? ",
            ui.span("Sign Up").text("red-500").cursor("pointer").font("medium").on_click(AuthController.toggle_view)
        ).text("sm").text_align("center").mt(4).text("gray-600")
    )

    # 2. Register Form
    register_form = ui.div(
        ui.h2("Create Account").text("2xl").font("bold").text_align("center").mb(6),
        
        ui.div(AuthState.error).bg("red-50").text("red-600").p(3).rounded("md").text("sm").mb(4) if AuthState.error else "",
        
        ui.input(type="email", placeholder="you@example.com").id("reg_email").w_full().p(2).border().rounded("md").mb(3),
        ui.input(type="password", placeholder="Password").id("reg_pass").w_full().p(2).border().rounded("md").mb(3),
        ui.input(type="password", placeholder="Confirm Password").id("reg_confirm").w_full().p(2).border().rounded("md").mb(6),
        
        ui.button("Create Account").w_full().bg("red-500").text("white").p(2).rounded("md").font("medium").hover("bg-red-600").transition()
            .on_click(AuthController.register, args=["reg_email.value", "reg_pass.value", "reg_confirm.value"]),
            
        ui.div(
            "Already have an account? ",
            ui.span("Sign In").text("red-500").cursor("pointer").font("medium").on_click(AuthController.toggle_view)
        ).text("sm").text_align("center").mt(4).text("gray-600")
    )
    
    # 3. Success State
    success_view = ui.div(
        ui.div(ui.i(data_lucide="check-circle").w(12).h(12).text("green-500")).flex().justify("center").mb(4),
        ui.h2("You are logged in!").text("2xl").font("bold").text_align("center").mb(2),
        ui.p(f"Welcome, {AuthState.user.email if AuthState.user else ''}").text_align("center").text("gray-600").mb(6),
        ui.button("Sign Out").w_full().bg("gray-200").text("gray-800").p(2).rounded("md").font("medium").hover("bg-gray-300").transition()
            .on_click(AuthController.logout)
    )

    # --- Assembly ---
    return ui.div(
        Card(
            # Switch content based on state
            success_view if AuthState.user else (login_form if AuthState.is_login_view else register_form)
        ).max_w("md").w_full().mx("auto").bg("white/80").backdrop_blur("md").shadow("xl")
    ).min_h("100vh").bg("gray-50").flex().items("center").justify("center").pt(20)
'''

# --- COMMANDS ---

@app.command()
def run(app_path: str = "main:app", host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """Run the PyX Application"""
    print(f"🚀 PyX Engine starting on http://{host}:{port}")
    uvicorn.run(app_path, host=host, port=port, reload=reload)


# =============================================================================
# BUILD & SSG COMMANDS
# =============================================================================

@app.command("build")
def build_static(
    output: str = "dist",
    pages: str = "pages",
    minify: bool = True,
    sitemap: bool = True,
    base_url: str = "/"
):
    """
    Build static site (SSG).
    
    Examples:
        pyx build
        pyx build --output out --no-minify
    """
    from .core.ssg import StaticSiteGenerator, BuildConfig
    
    config = BuildConfig(
        output_dir=output,
        pages_dir=pages,
        minify=minify,
        generate_sitemap=sitemap,
        base_url=base_url
    )
    
    ssg = StaticSiteGenerator(config)
    ssg.build()


@app.command("export")
def export_static(output: str = "dist"):
    """
    Export static site (alias for build).
    
    Example:
        pyx export
    """
    from .core.ssg import StaticSiteGenerator, BuildConfig
    
    config = BuildConfig(output_dir=output)
    ssg = StaticSiteGenerator(config)
    ssg.build()


@app.command("dev")
def dev_server(port: int = 3000, pages: str = "pages"):
    """
    Start development server with file-based routing.
    
    Example:
        pyx dev
        pyx dev --port 8080
    """
    print(f"\n🚀 PyX Dev Server")
    print(f"   http://localhost:{port}")
    print(f"   Pages: {pages}/\n")
    
    # Import and setup file router
    from .core.file_router import FileRouter
    
    router = FileRouter(pages)
    print("📄 Discovering routes:")
    routes = router.discover()
    
    print(f"\n✅ Found {len(routes)} routes\n")
    
    # Start uvicorn with auto-reload
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_dirs=[pages, "modules"]
    )


@app.command("preview")
def preview_build(port: int = 4000, dir: str = "dist"):
    """
    Preview built static site.
    
    Example:
        pyx preview
    """
    import http.server
    import socketserver
    
    os.chdir(dir)
    
    Handler = http.server.SimpleHTTPRequestHandler
    
    print(f"\n🔍 Previewing build from {dir}/")
    print(f"   http://localhost:{port}\n")
    
    with socketserver.TCPServer(("", port), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Preview server stopped")

@app.command()
def init(name: str):
    """Initialize a new PyX Project with Modular MVC Structure"""
    base_path = Path(name)
    if base_path.exists():
        print(f"Error: Directory '{name}' already exists.")
        return

    # Create Directories
    (base_path / "modules").mkdir(parents=True)
    (base_path / "assets").mkdir(parents=True)
    
    # Create main.py
    with open(base_path / "main.py", "w") as f:
        f.write(TEMPLATE_MAIN)
        
    print(f"Created project: {name}")
    
    # Create 'home' module
    _create_module(base_path, "home")
    
    print(f"✅ Project initialized! Run: cd {name} && pyx run")

@app.command(name="make:module")
def make_module(name: str):
    """Generate a new MVC Module"""
    base_path = Path(os.getcwd())
    
    # Check if inside a project (look for main.py or modules arg)
    if not (base_path / "modules").exists():
        # Fallback: maybe running from root, check if 'modules' dir exists
        if not (base_path / "modules").exists():
             print("Error: 'modules' directory not found. Are you in the project root?")
             return

    _create_module(base_path, name)

def _create_module(base_path: Path, name: str):
    module_path = base_path / "modules" / name
    if module_path.exists():
        print(f"Module '{name}' already exists.")
        return
        
    module_path.mkdir(parents=True)
    
    name_cap = name.capitalize()
    
    # Create Files
    with open(module_path / "state.py", "w") as f:
        f.write(TEMPLATE_STATE.format(name=name, name_cap=name_cap))
        
    with open(module_path / "controller.py", "w") as f:
        f.write(TEMPLATE_CONTROLLER.format(name=name, name_cap=name_cap))
        
    with open(module_path / "views.py", "w") as f:
        f.write(TEMPLATE_VIEW.format(name=name, name_cap=name_cap))
        
    with open(module_path / "__init__.py", "w") as f:
        f.write(TEMPLATE_INIT.format(name=name))
        
    print(f"📦 Module '{name}' created at modules/{name}/")

@app.command(name="make:auth")
def make_auth():
    """Generate a complete Authentication module (Login/Register)"""
    base_path = Path(os.getcwd())
    
    # Check if inside a project
    if not (base_path / "modules").exists():
         print("Error: 'modules' directory not found. Are you in the project root?")
         return

    module_path = base_path / "modules" / "auth"
    if module_path.exists():
        print(f"Module 'auth' already exists.")
        return
        
    module_path.mkdir(parents=True)
    
    # Create Files
    with open(module_path / "models.py", "w") as f:
        f.write(TEMPLATE_AUTH_MODEL)
        
    with open(module_path / "state.py", "w") as f:
        f.write(TEMPLATE_AUTH_STATE)
        
    with open(module_path / "controller.py", "w") as f:
        f.write(TEMPLATE_AUTH_CONTROLLER)
        
    with open(module_path / "views.py", "w") as f:
        f.write(TEMPLATE_AUTH_VIEW)
        
    with open(module_path / "__init__.py", "w") as f:
        f.write("from .views import auth_view\n")
        
    print(f"🔐 Auth module created at modules/auth/")
    print(f"   Next steps:")
    print(f"   1. Run 'pyx db init' (if not done)")
    print(f"   2. Run 'pyx db make-migrations 'Add auth users'")
    print(f"   3. Run 'pyx db migrate'")
    print(f"   4. Add route to main.py: app.add_page('/login', auth_view)")

@app.command()
@app.command()
def db_init():
    """Initialize Database Migrations (Alembic)"""
    import subprocess
    if not os.path.exists("migrations"):
        subprocess.run(["alembic", "init", "migrations"])
        
        # --- MAGIC: Inject SQLModel Metadata ---
        env_path = Path("migrations/env.py")
        if env_path.exists():
            content = env_path.read_text()
            
            # 1. Add SQLModel import
            if "from sqlmodel import SQLModel" not in content:
                content = content.replace(
                    "from logging.config import fileConfig",
                    "from logging.config import fileConfig\nfrom sqlmodel import SQLModel\nfrom pyx import Model  # Ensure models are loaded base"
                )
            
            # 2. Set target_metadata
            # Replace 'target_metadata = None' with 'target_metadata = SQLModel.metadata'
            content = content.replace("target_metadata = None", "target_metadata = SQLModel.metadata")
            
            # 3. Inject Model Auto-Discovery Code inside run_migrations_online/offline
            # Actually, simpler: just load models at top level so SQLModel.metadata is populated
            loader_code = """
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

# Auto-discover models in modules/
modules_dir = Path("modules")
if modules_dir.exists():
    for module in modules_dir.iterdir():
        if (module / "models.py").exists():
            try:
                __import__(f"modules.{module.name}.models")
            except Exception as e:
                print(f"Warning: Could not load models for {module.name}: {e}")
"""
            # Insert loader code after imports
            split_mark = "from logging.config import fileConfig"
            if split_mark in content:
                parts = content.split(split_mark)
                content = parts[0] + split_mark + "\n" + loader_code + parts[1]
                
            env_path.write_text(content)
            print("✨ Auto-configured migrations/env.py for PyX SQLModel.")

        # Update alembic.ini to use our db url (simple regex replace or just instruct user)
        # For now, we assume user sets it or we auto-set it later.
        print("✅ Migration environment initialized in /migrations")
    else:
        print("Warning: migrations/ folder already exists.")

@app.command()
def db_make_migrations(message: str = "Auto migration"):
    """Generate new migration file based on model changes"""
    import subprocess
    sys.path.append(os.getcwd())
    
    # Ensure models are loaded
    # Walk through modules/ to find models.py
    modules_dir = Path("modules")
    if modules_dir.exists():
        for module in modules_dir.iterdir():
            if (module / "models.py").exists():
                try:
                    # Import dynamic: modules.auth.models
                    __import__(f"modules.{module.name}.models")
                except Exception as e:
                    print(f"Warning: Could not load models for {module.name}: {e}")

    subprocess.run(["alembic", "revision", "--autogenerate", "-m", message])
    print(f"✅ Migration script created: {message}")

@app.command()
def db_migrate():
    """Apply pending migrations to Database"""
    import subprocess
    subprocess.run(["alembic", "upgrade", "head"])
    print("✅ Database upgraded to latest head.")

@app.command()
def create_admin(email: str):
    """Create an Admin User"""
    print(f"Creating admin user: {email}")
    # TODO: Implement actual User creation logic when Auth module is ready (Phase 2)
    print("User created! (Simulation)")


# =============================================================================
# PLUGIN MANAGEMENT COMMANDS
# =============================================================================

@app.command("add")
def add_plugin(name: str, version: str = None):
    """
    Install a PyX plugin.
    
    Examples:
        pyx add charts
        pyx add auth
        pyx add tailwind
    """
    from .core.plugins import PluginManager
    pm = PluginManager()
    pm.install(name, version)


@app.command("remove")
def remove_plugin(name: str):
    """
    Remove a PyX plugin.
    
    Example:
        pyx remove charts
    """
    from .core.plugins import PluginManager
    pm = PluginManager()
    pm.remove(name)


@app.command("plugins")
def list_plugins():
    """
    List installed PyX plugins.
    
    Example:
        pyx plugins
    """
    from .core.plugins import PluginManager
    pm = PluginManager()
    
    plugins = pm.list()
    
    if not plugins:
        print("📦 No plugins installed.")
        print("   Use 'pyx search' to find available plugins.")
        return
    
    print("📦 Installed plugins:\n")
    for p in plugins:
        print(f"  • {p.name} ({p.version})")
        print(f"    {p.description}")
        print()


@app.command("search")
def search_plugins(query: str = ""):
    """
    Search available PyX plugins.
    
    Examples:
        pyx search
        pyx search charts
    """
    from .core.plugins import PluginManager
    pm = PluginManager()
    
    results = pm.search(query)
    
    if not results:
        print(f"❌ No plugins found matching '{query}'")
        return
    
    print("🔍 Available plugins:\n")
    for p in results:
        status = "✅ installed" if p.get("installed") else ""
        print(f"  • {p['name']} ({p['version']}) {status}")
        print(f"    {p['description']}")
        print(f"    Type: {p['type']}")
        print()
    
    print("Install with: pyx add <plugin-name>")


@app.command("plugin-info")
def plugin_info(name: str):
    """
    Get detailed information about a plugin.
    
    Example:
        pyx plugin-info charts
    """
    from .core.plugins import PluginManager
    pm = PluginManager()
    
    info = pm.info(name)
    
    if not info:
        print(f"❌ Plugin '{name}' not found")
        return
    
    print(f"\n📦 Plugin: {info['name']}")
    print(f"   Version: {info['version']}")
    print(f"   Description: {info['description']}")
    print(f"   Type: {info['type']}")
    print(f"   Installed: {'Yes ✅' if info['installed'] else 'No'}")
    
    if info.get('pip_package'):
        print(f"   Pip Package: {info['pip_package']}")


@app.command("update")
def update_plugins(name: str = None):
    """
    Update installed plugin(s).
    
    Examples:
        pyx update           # Update all plugins
        pyx update charts    # Update specific plugin
    """
    from .core.plugins import PluginManager
    pm = PluginManager()
    
    if name:
        print(f"🔄 Updating plugin: {name}")
    else:
        print("🔄 Updating all plugins...")
    
    pm.update(name)
    print("✅ Update complete!")


# =============================================================================
# GENERATORS (pyx generate / pyx g)
# =============================================================================

generate_app = typer.Typer(help="Generate code scaffolds")
app.add_typer(generate_app, name="generate")
app.add_typer(generate_app, name="g")  # Shorthand


@generate_app.command("model")
def generate_model(
    name: str,
    fields: str = typer.Argument(None, help="Fields in format: name:str email:str age:int")
):
    """
    Generate a database model.
    
    Examples:
        pyx generate model User
        pyx generate model Post title:str content:str author_id:int
        pyx g model Product name:str price:float stock:int
    """
    # Parse fields
    field_list = []
    if fields:
        for field in fields.split():
            if ":" in field:
                fname, ftype = field.split(":", 1)
                field_list.append((fname, ftype))
    
    # Generate type mapping
    type_map = {
        "str": "str",
        "string": "str",
        "int": "int",
        "integer": "int",
        "float": "float",
        "bool": "bool",
        "boolean": "bool",
        "date": "datetime",
        "datetime": "datetime",
        "text": "str",
        "json": "dict",
    }
    
    # Build fields code
    fields_code = ""
    for fname, ftype in field_list:
        py_type = type_map.get(ftype.lower(), ftype)
        fields_code += f"    {fname}: {py_type} = db.Column()\n"
    
    if not fields_code:
        fields_code = "    # Add your fields here\n    # name: str = db.Column()\n    pass\n"
    
    name_cap = name.capitalize() if name[0].islower() else name
    name_lower = name.lower()
    
    template = f'''"""
Model: {name_cap}
Generated by PyX CLI
"""
from pyx import db
from typing import Optional, List
from datetime import datetime


class {name_cap}(db.Model, table=True):
    """Database model for {name_cap}"""
    
    id: Optional[int] = db.Column(primary_key=True)
{fields_code}
    created_at: datetime = db.CreatedAt()
    updated_at: datetime = db.UpdatedAt()
    
    def __repr__(self):
        return f"<{name_cap}(id={{self.id}})>"
'''
    
    # Determine output path
    models_dir = Path("models")
    if not models_dir.exists():
        models_dir.mkdir(parents=True)
        # Create __init__.py
        (models_dir / "__init__.py").write_text("# PyX Models\n")
    
    output_path = models_dir / f"{name_lower}.py"
    output_path.write_text(template)
    
    print(f"✅ Model created: {output_path}")
    print(f"   Import: from models.{name_lower} import {name_cap}")


@generate_app.command("page")
def generate_page(
    name: str,
    route: str = None
):
    """
    Generate a page component.
    
    Examples:
        pyx generate page dashboard
        pyx generate page about --route /about-us
        pyx g page settings
    """
    name_lower = name.lower().replace("-", "_")
    name_cap = "".join(word.capitalize() for word in name.split("_"))
    route_path = route or f"/{name_lower.replace('_', '-')}"
    
    template = f'''"""
Page: {name_cap}
Route: {route_path}
Generated by PyX CLI
"""
from pyx import ui


def {name_lower}_page():
    """
    {name_cap} page component.
    
    Route: {route_path}
    """
    return ui.container(
        # Header
        ui.div(
            ui.h1("{name_cap}").style(font="bold", text="3xl", color="gray-900"),
            ui.p("This is the {name_lower} page.").style(color="gray-600", mt=2),
        ).style(mb=8),
        
        # Content
        ui.card(
            ui.p("Edit pages/{name_lower}.py to customize this page.")
        ),
    ).style(py=8)


# Export for router
page = {name_lower}_page
'''
    
    # Determine output path
    pages_dir = Path("pages")
    if not pages_dir.exists():
        pages_dir.mkdir(parents=True)
    
    output_path = pages_dir / f"{name_lower}.py"
    output_path.write_text(template)
    
    print(f"✅ Page created: {output_path}")
    print(f"   Route: {route_path}")
    print(f"   Import: from pages.{name_lower} import page")


@generate_app.command("component")
def generate_component(
    name: str,
    props: str = typer.Argument(None, help="Props in format: title:str items:list")
):
    """
    Generate a reusable UI component.
    
    Examples:
        pyx generate component UserCard
        pyx generate component ProductList items:list
        pyx g component Header title:str
    """
    # Parse props
    prop_list = []
    if props:
        for prop in props.split():
            if ":" in prop:
                pname, ptype = prop.split(":", 1)
                prop_list.append((pname, ptype))
    
    name_cap = "".join(word.capitalize() for word in name.replace("-", "_").split("_"))
    name_lower = name.lower().replace("-", "_")
    
    # Build props signature
    props_sig = ""
    props_doc = ""
    for pname, ptype in prop_list:
        props_sig += f", {pname}: {ptype} = None"
        props_doc += f"        {pname}: {ptype}\n"
    
    if not props_doc:
        props_doc = "        (No props defined)\n"
    
    template = f'''"""
Component: {name_cap}
Generated by PyX CLI
"""
from pyx import ui
from typing import Any, List, Optional


def {name_cap}(className: str = ""{props_sig}):
    """
    {name_cap} component.
    
    Props:
{props_doc}
    Usage:
        {name_cap}()
        {name_cap}(className="custom-class")
    """
    return ui.div(
        # Component content
        ui.p("{name_cap} component"),
        
        # Use props here
        # ui.span(title) if title else None,
        
    ).cls(f"component-{name_lower} {{className}}")


# Export
{name_lower} = {name_cap}
'''
    
    # Determine output path
    components_dir = Path("components")
    if not components_dir.exists():
        components_dir.mkdir(parents=True)
        # Create __init__.py
        (components_dir / "__init__.py").write_text("# PyX Components\n")
    
    output_path = components_dir / f"{name_lower}.py"
    output_path.write_text(template)
    
    # Update __init__.py
    init_path = components_dir / "__init__.py"
    init_content = init_path.read_text()
    import_line = f"from .{name_lower} import {name_cap}"
    if import_line not in init_content:
        init_path.write_text(init_content + f"\n{import_line}\n")
    
    print(f"✅ Component created: {output_path}")
    print(f"   Import: from components import {name_cap}")


@generate_app.command("api")
def generate_api(
    name: str,
    crud: bool = typer.Option(False, "--crud", help="Generate full CRUD endpoints")
):
    """
    Generate API endpoints.
    
    Examples:
        pyx generate api users
        pyx generate api products --crud
        pyx g api posts --crud
    """
    name_lower = name.lower()
    name_cap = name.capitalize()
    name_singular = name_lower.rstrip("s")  # Simple singularize
    
    if crud:
        template = f'''"""
API: {name_cap}
Generated by PyX CLI (CRUD)
"""
from pyx import Router
from models.{name_singular} import {name_singular.capitalize()}
from pyx import db

router = Router()


@router.api("/api/{name_lower}", methods=["GET"])
def list_{name_lower}():
    """Get all {name_lower}"""
    items = db.find_all({name_singular.capitalize()})
    return {{"data": [item.__dict__ for item in items]}}


@router.api("/api/{name_lower}", methods=["POST"])
def create_{name_singular}(request):
    """Create new {name_singular}"""
    data = request.json
    item = {name_singular.capitalize()}(**data)
    db.save(item)
    return {{"data": item.__dict__}}, 201


@router.api("/api/{name_lower}/{{id}}", methods=["GET"])
def get_{name_singular}(id: int):
    """Get {name_singular} by ID"""
    item = db.get({name_singular.capitalize()}, id)
    if not item:
        return {{"error": "Not found"}}, 404
    return {{"data": item.__dict__}}


@router.api("/api/{name_lower}/{{id}}", methods=["PUT"])
def update_{name_singular}(id: int, request):
    """Update {name_singular}"""
    item = db.get({name_singular.capitalize()}, id)
    if not item:
        return {{"error": "Not found"}}, 404
    
    for key, value in request.json.items():
        setattr(item, key, value)
    db.save(item)
    return {{"data": item.__dict__}}


@router.api("/api/{name_lower}/{{id}}", methods=["DELETE"])  
def delete_{name_singular}(id: int):
    """Delete {name_singular}"""
    success = db.delete_by_id({name_singular.capitalize()}, id)
    if not success:
        return {{"error": "Not found"}}, 404
    return {{"message": "Deleted"}}, 204
'''
    else:
        template = f'''"""
API: {name_cap}
Generated by PyX CLI
"""
from pyx import Router

router = Router()


@router.api("/api/{name_lower}", methods=["GET"])
def get_{name_lower}():
    """Get {name_lower} endpoint"""
    return {{
        "message": "{name_cap} API",
        "data": []
    }}


@router.api("/api/{name_lower}", methods=["POST"])
def post_{name_lower}(request):
    """Create {name_lower} endpoint"""
    data = request.json
    # Process data here
    return {{"message": "Created", "data": data}}, 201
'''
    
    # Determine output path
    api_dir = Path("api")
    if not api_dir.exists():
        api_dir.mkdir(parents=True)
        (api_dir / "__init__.py").write_text("# PyX API Routes\n")
    
    output_path = api_dir / f"{name_lower}.py"
    output_path.write_text(template)
    
    print(f"✅ API created: {output_path}")
    print(f"   Endpoints: /api/{name_lower}")
    if crud:
        print(f"   Methods: GET, POST, PUT, DELETE (CRUD)")


@generate_app.command("test")
def generate_test(name: str):
    """
    Generate test file.
    
    Examples:
        pyx generate test users
        pyx g test auth
    """
    name_lower = name.lower()
    name_cap = name.capitalize()
    
    template = f'''"""
Tests: {name_cap}
Generated by PyX CLI
"""
from pyx import test


class Test{name_cap}:
    """Test suite for {name_lower}"""
    
    def setup_method(self):
        """Setup before each test"""
        pass
    
    def teardown_method(self):
        """Cleanup after each test"""
        pass
    
    def test_example(self):
        """Example test case"""
        assert True
    
    # Add more tests here
    # def test_{name_lower}_creation(self):
    #     pass


# Run with: pyx test tests/test_{name_lower}.py
'''
    
    # Determine output path
    tests_dir = Path("tests")
    if not tests_dir.exists():
        tests_dir.mkdir(parents=True)
        # Create conftest.py
        conftest = '''"""
PyX Test Configuration
"""
import pytest
from pyx import test, db


@pytest.fixture(scope="session")
def app():
    """Create test app"""
    from main import app
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return test.client(app)


@pytest.fixture(scope="function")
def database():
    """Create test database"""
    with test.database() as db:
        yield db
'''
        (tests_dir / "conftest.py").write_text(conftest)
        (tests_dir / "__init__.py").write_text("")
    
    output_path = tests_dir / f"test_{name_lower}.py"
    output_path.write_text(template)
    
    print(f"✅ Test created: {output_path}")
    print(f"   Run: pyx test tests/test_{name_lower}.py")


@generate_app.command("migration")
def generate_migration(name: str):
    """
    Generate database migration.
    
    Examples:
        pyx generate migration add_users_table
        pyx g migration add_email_to_users
    """
    from datetime import datetime
    
    migrations_dir = Path("migrations")
    if not migrations_dir.exists():
        migrations_dir.mkdir(parents=True)
        (migrations_dir / "__init__.py").write_text("# PyX Migrations\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{name}.py"
    
    template = f'''"""
Migration: {name}
Created: {datetime.now().isoformat()}
"""
from pyx import db


def up():
    """Apply migration"""
    # Example:
    # db.raw("""
    #     CREATE TABLE users (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         name VARCHAR(255),
    #         email VARCHAR(255) UNIQUE
    #     )
    # """)
    pass


def down():
    """Rollback migration"""
    # Example:
    # db.raw("DROP TABLE IF EXISTS users")
    pass
'''
    
    output_path = migrations_dir / filename
    output_path.write_text(template)
    
    print(f"✅ Migration created: {output_path}")
    print(f"   Apply: pyx migrate up")


# =============================================================================
# TEST COMMAND
# =============================================================================

@app.command("test")
def run_tests(
    path: str = "tests",
    verbose: bool = True,
    coverage: bool = False
):
    """
    Run tests.
    
    Examples:
        pyx test
        pyx test tests/test_users.py
        pyx test --coverage
    """
    import subprocess
    import sys
    
    cmd = [sys.executable, "-m", "pytest", path]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html"])
        print("📊 Coverage report will be in htmlcov/")
    
    print(f"🧪 Running tests in {path}/\n")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")


@generate_app.command("docker")
def generate_docker():
    """
    Generate Dockerfile and .dockerignore for deployment.
    
    Example:
        pyx generate docker
    """
    dockerfile = '''# Generated by PyX CLI
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
# Note: Ensure you have requirements.txt
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Build static assets (optional, uncomment if needed)
# RUN pyx build

# Expose default port
EXPOSE 8000

# Run the application
CMD ["pyx", "run", "--host", "0.0.0.0", "--port", "8000", "--no-reload"]
'''

    dockerignore = '''__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env
.git
.gitignore
.dockerignore
dist/
build/
*.egg-info/
.DS_Store
'''

    path_dockerfile = Path("Dockerfile")
    path_ignore = Path(".dockerignore")
    
    if path_dockerfile.exists():
        print("⚠️  Dockerfile already exists")
    else:
        path_dockerfile.write_text(dockerfile)
        print("✅ Dockerfile created")

    if path_ignore.exists():
        print("⚠️  .dockerignore already exists")
    else:
        path_ignore.write_text(dockerignore)
        print("✅ .dockerignore created")
        
    print("\n🚀 Ready to deploy!")
    print("   1. Build: docker build -t myapp .")
    print("   2. Run:   docker run -p 8000:8000 myapp")


# =============================================================================
# =============================================================================
# DATABASE COMMANDS (Reflex-style)
# =============================================================================

# Create a subcommand group for database operations
db_app = typer.Typer(help="Database management commands")
app.add_typer(db_app, name="db")


@db_app.command("init")
def db_init():
    """
    Initialize database and Alembic migrations.
    
    This creates:
    - alembic/ directory with migration scripts
    - alembic.ini configuration file
    - Initial migration with current models
    
    Example:
        pyx db init
    """
    import subprocess
    
    print("📦 Initializing database migrations...")
    
    # Check if alembic is installed
    try:
        import alembic
    except ImportError:
        print("❌ Alembic not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "alembic"], check=True)
    
    # Check if alembic directory exists
    if os.path.exists("alembic"):
        print("⚠️  Alembic already initialized. Use 'pyx db makemigrations' to create new migrations.")
        return
    
    # Initialize alembic
    subprocess.run(["alembic", "init", "alembic"], check=True)
    
    # Update alembic/env.py to use our models
    env_path = Path("alembic/env.py")
    if env_path.exists():
        content = env_path.read_text()
        
        # Add our imports and configuration
        new_imports = """
# PyX Database Integration
from pyx.core.database import DatabaseConfig, Model
from sqlmodel import SQLModel

# Import all your models here to ensure they're registered
# Example: from app.models import User, Post

target_metadata = SQLModel.metadata
"""
        
        # Replace target_metadata = None with our version
        content = content.replace("target_metadata = None", new_imports)
        env_path.write_text(content)
    
    print("✅ Database migrations initialized!")
    print("\n📝 Next steps:")
    print("   1. Import your models in alembic/env.py")
    print("   2. Run 'pyx db makemigrations -m \"initial\"' to create first migration")
    print("   3. Run 'pyx db migrate' to apply migrations")


@db_app.command("makemigrations")
def db_makemigrations(
    message: str = typer.Option("auto", "-m", "--message", help="Migration message")
):
    """
    Generate a new migration script based on model changes.
    
    Example:
        pyx db makemigrations -m "add user table"
    """
    import subprocess
    
    if not os.path.exists("alembic"):
        print("❌ Alembic not initialized. Run 'pyx db init' first.")
        return
    
    print(f"📦 Creating migration: {message}")
    result = subprocess.run(
        ["alembic", "revision", "--autogenerate", "-m", message],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Migration created!")
        print(result.stdout)
    else:
        print("❌ Migration failed:")
        print(result.stderr)


@db_app.command("migrate")
def db_migrate(
    revision: str = typer.Argument("head", help="Target revision (default: head)")
):
    """
    Apply pending migrations to the database.
    
    Examples:
        pyx db migrate          # Apply all pending
        pyx db migrate head     # Apply all pending
        pyx db migrate +1       # Apply next migration
        pyx db migrate abc123   # Apply up to specific revision
    """
    import subprocess
    
    if not os.path.exists("alembic"):
        print("❌ Alembic not initialized. Run 'pyx db init' first.")
        return
    
    print(f"📦 Applying migrations to: {revision}")
    result = subprocess.run(
        ["alembic", "upgrade", revision],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Migrations applied!")
        print(result.stdout)
    else:
        print("❌ Migration failed:")
        print(result.stderr)


@db_app.command("rollback")
def db_rollback(
    steps: int = typer.Argument(1, help="Number of migrations to rollback")
):
    """
    Rollback migrations.
    
    Examples:
        pyx db rollback      # Rollback 1 migration
        pyx db rollback 2    # Rollback 2 migrations
    """
    import subprocess
    
    if not os.path.exists("alembic"):
        print("❌ Alembic not initialized. Run 'pyx db init' first.")
        return
    
    print(f"📦 Rolling back {steps} migration(s)...")
    result = subprocess.run(
        ["alembic", "downgrade", f"-{steps}"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Rollback complete!")
        print(result.stdout)
    else:
        print("❌ Rollback failed:")
        print(result.stderr)


@db_app.command("history")
def db_history():
    """
    Show migration history.
    
    Example:
        pyx db history
    """
    import subprocess
    
    if not os.path.exists("alembic"):
        print("❌ Alembic not initialized. Run 'pyx db init' first.")
        return
    
    result = subprocess.run(
        ["alembic", "history", "--verbose"],
        capture_output=True,
        text=True
    )
    print(result.stdout)


@db_app.command("current")
def db_current():
    """
    Show current migration revision.
    
    Example:
        pyx db current
    """
    import subprocess
    
    if not os.path.exists("alembic"):
        print("❌ Alembic not initialized. Run 'pyx db init' first.")
        return
    
    result = subprocess.run(
        ["alembic", "current"],
        capture_output=True,
        text=True
    )
    print(result.stdout)


@db_app.command("create-tables")
def db_create_tables():
    """
    Create all tables without migrations (development only).
    
    WARNING: This bypasses Alembic and creates tables directly.
    Use only for quick prototyping.
    
    Example:
        pyx db create-tables
    """
    from .core.database import create_tables
    
    print("⚠️  Creating tables directly (bypassing migrations)...")
    create_tables()
    print("✅ Tables created!")


# Legacy migrate command for backwards compatibility
@app.command("migrate")
def run_migration(
    direction: str = typer.Argument("up", help="Direction: up or down")
):
    """
    [DEPRECATED] Use 'pyx db migrate' instead.
    
    Run database migrations.
    """
    print("⚠️  'pyx migrate' is deprecated. Use 'pyx db migrate' instead.\n")
    
    if direction == "up":
        db_migrate("head")
    elif direction == "down":
        db_rollback(1)
    else:
        print(f"Unknown direction: {direction}. Use 'up' or 'down'")


def main():
    app()

if __name__ == "__main__":
    main()

