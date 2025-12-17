"""
PyX Internationalization (i18n)
Multi-language support for PyX applications.
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from functools import wraps


@dataclass
class Locale:
    """Locale configuration"""
    code: str           # 'en', 'id', 'ja'
    name: str           # 'English', 'Bahasa Indonesia', '日本語'
    direction: str = "ltr"  # 'ltr' or 'rtl'
    flag: str = ""      # Emoji flag '🇺🇸', '🇮🇩'


class I18n:
    """
    Internationalization manager.
    
    Usage:
        # Setup
        from pyx import i18n
        
        i18n.load_translations("locales")
        i18n.set_locale("id")
        
        # In components
        from pyx import t
        
        def my_page():
            return ui.div(
                ui.h1(t("welcome")),  # "Selamat Datang"
                ui.p(t("description"))
            )
        
        # With variables
        t("greeting", name="John")  # "Hello, John!"
        
        # Pluralization
        t("items", count=5)  # "5 items"
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._translations: Dict[str, Dict[str, Any]] = {}
        self._current_locale: str = "en"
        self._fallback_locale: str = "en"
        self._locales: Dict[str, Locale] = {}
        self._initialized = True
        
        # Default locales
        self.add_locale(Locale("en", "English", flag="🇺🇸"))
        self.add_locale(Locale("id", "Bahasa Indonesia", flag="🇮🇩"))
        self.add_locale(Locale("ja", "日本語", flag="🇯🇵"))
        self.add_locale(Locale("zh", "中文", flag="🇨🇳"))
        self.add_locale(Locale("ar", "العربية", direction="rtl", flag="🇸🇦"))
    
    def add_locale(self, locale: Locale):
        """Add a supported locale"""
        self._locales[locale.code] = locale
    
    def load_translations(self, directory: str = "locales"):
        """
        Load translation files from directory.
        
        Expected structure:
            locales/
            ├── en.json
            ├── id.json
            └── ja.json
        
        JSON format:
            {
                "welcome": "Welcome",
                "greeting": "Hello, {name}!",
                "items": {
                    "one": "{count} item",
                    "other": "{count} items"
                }
            }
        """
        locales_path = Path(directory)
        
        if not locales_path.exists():
            print(f"⚠️  Locales directory '{directory}' not found")
            return
        
        for file in locales_path.glob("*.json"):
            locale_code = file.stem
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    self._translations[locale_code] = json.load(f)
                print(f"   📄 Loaded {locale_code}.json")
            except Exception as e:
                print(f"   ⚠️ Error loading {file}: {e}")
    
    def set_locale(self, locale: str):
        """Set the current locale"""
        if locale in self._locales or locale in self._translations:
            self._current_locale = locale
        else:
            print(f"⚠️  Locale '{locale}' not found, using fallback '{self._fallback_locale}'")
    
    def get_locale(self) -> str:
        """Get current locale code"""
        return self._current_locale
    
    def get_locale_info(self) -> Locale:
        """Get current locale info"""
        return self._locales.get(self._current_locale, self._locales.get("en"))
    
    def get_direction(self) -> str:
        """Get text direction for current locale"""
        locale = self.get_locale_info()
        return locale.direction if locale else "ltr"
    
    def translate(self, key: str, **kwargs) -> str:
        """
        Translate a key with optional variables.
        
        Usage:
            i18n.translate("welcome")
            i18n.translate("greeting", name="John")
            i18n.translate("items", count=5)
        """
        # Get translations for current locale, fallback to default
        translations = self._translations.get(
            self._current_locale, 
            self._translations.get(self._fallback_locale, {})
        )
        
        # Navigate nested keys (e.g., "nav.home")
        value = translations
        for part in key.split("."):
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break
        
        if value is None:
            # Key not found, return key itself
            return key
        
        # Handle pluralization
        if isinstance(value, dict) and "count" in kwargs:
            count = kwargs["count"]
            if count == 1 and "one" in value:
                value = value["one"]
            elif count == 0 and "zero" in value:
                value = value["zero"]
            else:
                value = value.get("other", value.get("many", str(value)))
        
        # Substitute variables
        if isinstance(value, str):
            try:
                return value.format(**kwargs)
            except KeyError:
                return value
        
        return str(value)
    
    def t(self, key: str, **kwargs) -> str:
        """Shorthand for translate"""
        return self.translate(key, **kwargs)
    
    def available_locales(self) -> List[Locale]:
        """Get list of available locales"""
        return list(self._locales.values())
    
    def language_switcher(self, className: str = "") -> str:
        """
        Generate a language switcher component.
        
        Usage:
            i18n.language_switcher()
        """
        options = ""
        for code, locale in self._locales.items():
            if code in self._translations:
                selected = "selected" if code == self._current_locale else ""
                options += f'<option value="{code}" {selected}>{locale.flag} {locale.name}</option>'
        
        return f'''
        <select onchange="PyxI18n.setLocale(this.value)" class="px-3 py-2 border rounded-lg {className}">
            {options}
        </select>
        
        <script>
            window.PyxI18n = window.PyxI18n || {{
                setLocale: function(locale) {{
                    document.cookie = 'pyx_locale=' + locale + ';path=/;max-age=31536000';
                    location.reload();
                }}
            }};
        </script>
        '''


# Global instance
i18n = I18n()


def t(key: str, **kwargs) -> str:
    """
    Translate helper function.
    
    Usage:
        from pyx import t
        
        t("welcome")
        t("greeting", name="John")
        t("items", count=5)
    """
    return i18n.translate(key, **kwargs)


def locale(code: str):
    """
    Decorator to set locale for a page.
    
    Usage:
        @locale("id")
        def indonesian_page():
            return ui.div(t("welcome"))
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            original_locale = i18n.get_locale()
            i18n.set_locale(code)
            try:
                return func(*args, **kwargs)
            finally:
                i18n.set_locale(original_locale)
        return wrapper
    return decorator


class LocaleMiddleware:
    """
    Middleware to detect and set locale from request.
    
    Detection order:
    1. URL parameter (?lang=id)
    2. Cookie (pyx_locale)
    3. Accept-Language header
    4. Default locale
    """
    
    async def __call__(self, request, next_handler):
        # 1. Check URL parameter
        locale_code = request.query_params.get("lang")
        
        # 2. Check cookie
        if not locale_code:
            locale_code = request.cookies.get("pyx_locale")
        
        # 3. Check Accept-Language header
        if not locale_code:
            accept_lang = request.headers.get("accept-language", "")
            if accept_lang:
                # Parse first language
                locale_code = accept_lang.split(",")[0].split("-")[0].strip()
        
        # 4. Set locale
        if locale_code:
            i18n.set_locale(locale_code)
        
        return await next_handler(request)


def create_translation_files(directory: str = "locales", locales: List[str] = None):
    """
    CLI helper to create translation file templates.
    
    Usage:
        create_translation_files("locales", ["en", "id", "ja"])
    """
    locales = locales or ["en", "id"]
    locales_path = Path(directory)
    locales_path.mkdir(parents=True, exist_ok=True)
    
    template = {
        "common": {
            "app_name": "My App",
            "loading": "Loading...",
            "error": "An error occurred",
            "success": "Success!",
            "cancel": "Cancel",
            "save": "Save",
            "delete": "Delete",
            "edit": "Edit",
            "back": "Back",
            "next": "Next",
            "submit": "Submit"
        },
        "nav": {
            "home": "Home",
            "about": "About",
            "contact": "Contact",
            "login": "Login",
            "logout": "Logout"
        },
        "auth": {
            "login": "Login",
            "register": "Register",
            "email": "Email",
            "password": "Password",
            "forgot_password": "Forgot Password?",
            "remember_me": "Remember Me"
        },
        "errors": {
            "404": "Page not found",
            "500": "Server error",
            "required": "This field is required",
            "invalid_email": "Please enter a valid email"
        }
    }
    
    for locale_code in locales:
        file_path = locales_path / f"{locale_code}.json"
        if not file_path.exists():
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            print(f"✅ Created {file_path}")
        else:
            print(f"⚠️  {file_path} already exists, skipping")
