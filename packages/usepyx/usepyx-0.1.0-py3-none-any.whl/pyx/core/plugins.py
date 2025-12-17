"""
PyX Plugin System
Extensible plugin architecture for PyX framework.
"""
import os
import sys
import json
import shutil
import subprocess
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path


# Plugin registry file location
PLUGINS_FILE = ".pyx/plugins.json"
PLUGINS_DIR = ".pyx/plugins"


@dataclass
class PluginInfo:
    """Information about a plugin"""
    name: str
    version: str
    description: str = ""
    author: str = ""
    homepage: str = ""
    dependencies: List[str] = field(default_factory=list)
    entry_point: str = "plugin.py"  # Main plugin file
    type: str = "component"  # "component", "lib", "theme", "cli"
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "homepage": self.homepage,
            "dependencies": self.dependencies,
            "entry_point": self.entry_point,
            "type": self.type,
        }
    
    @staticmethod
    def from_dict(data: Dict) -> "PluginInfo":
        return PluginInfo(**data)


class PluginRegistry:
    """
    Central registry for installed plugins.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.plugins_file = self.project_root / PLUGINS_FILE
        self.plugins_dir = self.project_root / PLUGINS_DIR
        self._plugins: Dict[str, PluginInfo] = {}
        self._loaded: Dict[str, Any] = {}
        self._load_registry()
    
    def _load_registry(self):
        """Load installed plugins from registry file"""
        if self.plugins_file.exists():
            try:
                with open(self.plugins_file) as f:
                    data = json.load(f)
                    for name, info in data.get("plugins", {}).items():
                        self._plugins[name] = PluginInfo.from_dict(info)
            except:
                pass
    
    def _save_registry(self):
        """Save registry to file"""
        self.plugins_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "plugins": {name: info.to_dict() for name, info in self._plugins.items()}
        }
        with open(self.plugins_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def register(self, plugin: PluginInfo):
        """Register a new plugin"""
        self._plugins[plugin.name] = plugin
        self._save_registry()
    
    def unregister(self, name: str):
        """Unregister a plugin"""
        if name in self._plugins:
            del self._plugins[name]
            self._save_registry()
    
    def get(self, name: str) -> Optional[PluginInfo]:
        """Get plugin info by name"""
        return self._plugins.get(name)
    
    def list_all(self) -> List[PluginInfo]:
        """List all registered plugins"""
        return list(self._plugins.values())
    
    def is_installed(self, name: str) -> bool:
        """Check if plugin is installed"""
        return name in self._plugins


class PluginLoader:
    """
    Dynamic plugin loader.
    """
    
    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self._hooks: Dict[str, List[Callable]] = {}
    
    def load(self, name: str) -> Any:
        """Load a plugin module"""
        if name in self.registry._loaded:
            return self.registry._loaded[name]
        
        plugin_info = self.registry.get(name)
        if not plugin_info:
            raise ValueError(f"Plugin '{name}' not found")
        
        # Find plugin directory
        plugin_dir = self.registry.plugins_dir / name
        if not plugin_dir.exists():
            raise ValueError(f"Plugin directory not found: {plugin_dir}")
        
        # Add to path and import
        sys.path.insert(0, str(plugin_dir))
        try:
            entry_point = plugin_info.entry_point.replace(".py", "")
            module = __import__(entry_point)
            self.registry._loaded[name] = module
            
            # Call setup if exists
            if hasattr(module, 'setup'):
                module.setup()
            
            return module
        finally:
            sys.path.remove(str(plugin_dir))
    
    def load_all(self):
        """Load all installed plugins"""
        for plugin in self.registry.list_all():
            try:
                self.load(plugin.name)
            except Exception as e:
                print(f"Warning: Failed to load plugin '{plugin.name}': {e}")
    
    def register_hook(self, hook_name: str, callback: Callable):
        """Register a callback for a hook"""
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(callback)
    
    def trigger_hook(self, hook_name: str, *args, **kwargs):
        """Trigger all callbacks for a hook"""
        results = []
        for callback in self._hooks.get(hook_name, []):
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"Hook error: {e}")
        return results


class PluginManager:
    """
    High-level plugin management.
    
    Usage:
        pm = PluginManager()
        pm.install("charts")
        pm.list()
        pm.remove("charts")
    """
    
    # Official PyX plugin repository (future)
    OFFICIAL_PLUGINS = {
        "charts": {
            "name": "charts",
            "version": "1.0.0",
            "description": "Advanced charting components (AG Charts)",
            "type": "component",
            "pip_package": "pyx-charts",
        },
        "auth": {
            "name": "auth",
            "version": "1.0.0", 
            "description": "Authentication & authorization utilities",
            "type": "lib",
            "pip_package": "pyx-auth",
        },
        "tailwind": {
            "name": "tailwind",
            "version": "1.0.0",
            "description": "Tailwind CSS integration",
            "type": "theme",
            "pip_package": "pyx-tailwind",
        },
        "icons": {
            "name": "icons",
            "version": "1.0.0",
            "description": "Extended icon packs (Heroicons, Phosphor, etc.)",
            "type": "component",
            "pip_package": "pyx-icons",
        },
        "forms": {
            "name": "forms",
            "version": "1.0.0",
            "description": "Advanced form components",
            "type": "component",
            "pip_package": "pyx-forms",
        },
        "admin": {
            "name": "admin",
            "version": "1.0.0",
            "description": "Admin dashboard generator",
            "type": "lib",
            "pip_package": "pyx-admin",
        },
    }
    
    def __init__(self, project_root: str = "."):
        self.registry = PluginRegistry(project_root)
        self.loader = PluginLoader(self.registry)
    
    def install(self, name: str, version: str = None) -> bool:
        """
        Install a plugin.
        
        Usage:
            pm.install("charts")
            pm.install("charts", version="1.0.0")
        """
        print(f"📦 Installing plugin: {name}")
        
        # Check if already installed
        if self.registry.is_installed(name):
            print(f"  ⚠️  Plugin '{name}' is already installed")
            return False
        
        # Check if it's an official plugin
        if name in self.OFFICIAL_PLUGINS:
            plugin_data = self.OFFICIAL_PLUGINS[name]
            
            # Install pip package if specified
            if plugin_data.get("pip_package"):
                pip_package = plugin_data["pip_package"]
                print(f"  📥 Installing pip package: {pip_package}")
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", pip_package],
                        check=True,
                        capture_output=True
                    )
                except subprocess.CalledProcessError as e:
                    print(f"  ❌ Failed to install pip package: {e}")
                    # Continue anyway for local development
            
            # Create plugin entry
            plugin_info = PluginInfo(
                name=name,
                version=version or plugin_data["version"],
                description=plugin_data["description"],
                type=plugin_data["type"],
            )
            
            # Create plugin directory
            plugin_dir = self.registry.plugins_dir / name
            plugin_dir.mkdir(parents=True, exist_ok=True)
            
            # Create basic plugin file
            plugin_file = plugin_dir / "plugin.py"
            plugin_file.write_text(f'''"""
PyX Plugin: {name}
{plugin_data["description"]}
"""

def setup():
    """Called when plugin is loaded"""
    print("Plugin {name} loaded!")

def get_components():
    """Return components provided by this plugin"""
    return {{}}
''')
            
            self.registry.register(plugin_info)
            print(f"  ✅ Plugin '{name}' installed successfully!")
            return True
        
        else:
            print(f"  ❌ Unknown plugin: {name}")
            print(f"  Available plugins: {', '.join(self.OFFICIAL_PLUGINS.keys())}")
            return False
    
    def remove(self, name: str) -> bool:
        """Remove a plugin"""
        print(f"🗑️  Removing plugin: {name}")
        
        if not self.registry.is_installed(name):
            print(f"  ⚠️  Plugin '{name}' is not installed")
            return False
        
        # Remove plugin directory
        plugin_dir = self.registry.plugins_dir / name
        if plugin_dir.exists():
            shutil.rmtree(plugin_dir)
        
        # Unregister
        self.registry.unregister(name)
        print(f"  ✅ Plugin '{name}' removed successfully!")
        return True
    
    def list(self) -> List[PluginInfo]:
        """List installed plugins"""
        return self.registry.list_all()
    
    def search(self, query: str = "") -> List[Dict]:
        """Search available plugins"""
        results = []
        for name, info in self.OFFICIAL_PLUGINS.items():
            if query.lower() in name.lower() or query.lower() in info["description"].lower():
                installed = self.registry.is_installed(name)
                results.append({
                    **info,
                    "installed": installed
                })
        return results
    
    def update(self, name: str = None) -> bool:
        """Update plugin(s)"""
        if name:
            plugins = [name]
        else:
            plugins = [p.name for p in self.registry.list_all()]
        
        for plugin_name in plugins:
            if self.registry.is_installed(plugin_name):
                print(f"🔄 Updating {plugin_name}...")
                # For now, just reinstall
                self.remove(plugin_name)
                self.install(plugin_name)
        
        return True
    
    def info(self, name: str) -> Optional[Dict]:
        """Get plugin information"""
        if name in self.OFFICIAL_PLUGINS:
            info = self.OFFICIAL_PLUGINS[name].copy()
            info["installed"] = self.registry.is_installed(name)
            return info
        return None


# Global plugin manager instance
plugins = PluginManager()


def use_plugin(name: str):
    """
    Decorator to require a plugin.
    
    Usage:
        @use_plugin("charts")
        def my_chart_page():
            return AdvancedChart(...)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not plugins.registry.is_installed(name):
                raise RuntimeError(f"Plugin '{name}' is required but not installed. Run: pyx add {name}")
            plugins.loader.load(name)
            return func(*args, **kwargs)
        return wrapper
    return decorator
