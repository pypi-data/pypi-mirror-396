import json

class JS:
    """
    Helper to generate client-side JavaScript for PyX.
    Allows "Zen Mode" like syntax for simple DOM manipulations without server round-trips.
    """
    def __init__(self, code=""):
        self.code = code
    
    def __str__(self):
        return self.code

    def _chain(self, code):
        """Append code to current chain"""
        separator = "; " if self.code else ""
        return JS(self.code + separator + code)

    # =========================================================================
    # DOM MANIPULATION
    # =========================================================================
    
    @staticmethod
    def toggle_class(selector: str, class_name: str):
        """Toggle a CSS class on element(s) matching the selector."""
        return JS(f"document.querySelectorAll('{selector}').forEach(el => el.classList.toggle('{class_name}'))")

    @staticmethod
    def add_class(selector: str, class_name: str):
        """Add a CSS class to element(s)."""
        return JS(f"document.querySelectorAll('{selector}').forEach(el => el.classList.add('{class_name}'))")

    @staticmethod
    def remove_class(selector: str, class_name: str):
        """Remove a CSS class from element(s)."""
        return JS(f"document.querySelectorAll('{selector}').forEach(el => el.classList.remove('{class_name}'))")
    
    @staticmethod
    def set_text(selector: str, text: str):
        """Set text content of element(s)."""
        # Escaping text for JS string safety
        safe_text = json.dumps(text)[1:-1]
        return JS(f"document.querySelectorAll('{selector}').forEach(el => el.innerText = '{safe_text}')")
    
    @staticmethod
    def set_value(selector: str, value: str):
        """Set value of input element(s)."""
        safe_val = json.dumps(value)[1:-1]
        return JS(f"document.querySelectorAll('{selector}').forEach(el => el.value = '{safe_val}')")

    @staticmethod
    def remove(selector: str):
        """Remove element(s) from DOM."""
        return JS(f"document.querySelectorAll('{selector}').forEach(el => el.remove())")

    # =========================================================================
    # UTILITIES
    # =========================================================================

    @staticmethod
    def navigate(url: str):
        """Client-side navigation (SPA)."""
        return JS(f"PyX.navigate('{url}')")
    
    @staticmethod
    def toast(message: str, variant: str = "info"):
        """Show a toast notification."""
        return JS(f"PyX.toast('{message}', '{variant}')")
    
    @staticmethod
    def copy_to_clipboard(text: str):
        """Copy text to clipboard."""
        safe_text = json.dumps(text)[1:-1]
        return JS(f"navigator.clipboard.writeText('{safe_text}')")
        
    @staticmethod
    def eval(code: str) -> 'JS':
        """Execute raw JavaScript"""
        return JS(code)

    @staticmethod
    def log(message: str) -> 'JS':
        """Console log."""
        safe_msg = json.dumps(message)[1:-1]
        return JS(f"console.log('{safe_msg}')")

    # =========================================================================
    # CHAINING METHODS (Instance Methods)
    # =========================================================================
    
    def toggle(self, selector: str, class_name: str):
        return self._chain(f"document.querySelectorAll('{selector}').forEach(el => el.classList.toggle('{class_name}'))")
        
    def add(self, selector: str, class_name: str):
        return self._chain(f"document.querySelectorAll('{selector}').forEach(el => el.classList.add('{class_name}'))")
        
    def rem(self, selector: str, class_name: str):
        return self._chain(f"document.querySelectorAll('{selector}').forEach(el => el.classList.remove('{class_name}'))")
    
    def then_toast(self, message: str, variant: str = "info"):
        return self._chain(f"PyX.toast('{message}', '{variant}')")
        
    def then_navigate(self, url: str):
        return self._chain(f"PyX.navigate('{url}')")


# ==========================================
# CLIENT STORAGE
# ==========================================

class ClientStorage:
    """
    Sync Python values with browser localStorage.
    
    Usage:
        storage = ClientStorage()
        
        # Set value (syncs to browser)
        storage.set("theme", "dark")
        
        # Get value (from server-side cache, use with on_mount for initial load)
        theme = storage.get("theme", default="light")
        
        # In View - Generate JS to read from localStorage
        ui.div().attr("x-data", storage.alpine_init("theme", "light"))
    """
    _cache: dict = {}
    
    @staticmethod
    def set(key: str, value) -> 'JS':
        """Set a value in localStorage (returns JS action)"""
        import json
        safe_value = json.dumps(value)
        ClientStorage._cache[key] = value
        return JS(f"localStorage.setItem('{key}', {safe_value})")
    
    @staticmethod
    def get(key: str, default=None):
        """Get value from server-side cache (call after on_mount sync)"""
        return ClientStorage._cache.get(key, default)
    
    @staticmethod
    def remove(key: str) -> 'JS':
        """Remove a value from localStorage"""
        if key in ClientStorage._cache:
            del ClientStorage._cache[key]
        return JS(f"localStorage.removeItem('{key}')")
    
    @staticmethod
    def clear() -> 'JS':
        """Clear all localStorage"""
        ClientStorage._cache = {}
        return JS("localStorage.clear()")
    
    @staticmethod
    def sync_to_server(key: str) -> 'JS':
        """
        Generate JS that sends localStorage value to server.
        Use in on_mount to hydrate server-side cache.
        """
        return JS(f"""
            (function() {{
                const val = localStorage.getItem('{key}');
                if (val && window.ws && window.ws.readyState === WebSocket.OPEN) {{
                    window.ws.send(JSON.stringify({{
                        type: 'storage_sync',
                        key: '{key}',
                        value: val
                    }}));
                }}
            }})()
        """)
    
    @staticmethod
    def alpine_init(key: str, default="") -> str:
        """
        Generate Alpine.js x-data initializer that reads from localStorage.
        Useful for client-side reactive state without server round-trip.
        
        Example:
            ui.div().attr("x-data", storage.alpine_init("count", 0))
        """
        import json
        safe_default = json.dumps(default)
        return f"{{ {key}: JSON.parse(localStorage.getItem('{key}')) || {safe_default} }}"


# Singleton instance
storage = ClientStorage()
