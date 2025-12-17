"""
PyX Theme System
Centralized theming with dark mode support.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import json


@dataclass
class ThemeColors:
    """Color palette for a theme"""
    # Brand
    primary: str = "#3b82f6"  # Blue
    secondary: str = "#6366f1"  # Indigo
    accent: str = "#f59e0b"  # Amber
    
    # Semantic
    success: str = "#22c55e"
    warning: str = "#f59e0b"
    error: str = "#ef4444"
    info: str = "#3b82f6"
    
    # Neutral
    background: str = "#ffffff"
    foreground: str = "#0f172a"
    card: str = "#ffffff"
    card_foreground: str = "#0f172a"
    muted: str = "#f1f5f9"
    muted_foreground: str = "#64748b"
    border: str = "#e2e8f0"
    input: str = "#e2e8f0"
    ring: str = "#3b82f6"


@dataclass
class ThemeSpacing:
    """Spacing scale"""
    xs: str = "0.25rem"
    sm: str = "0.5rem"
    md: str = "1rem"
    lg: str = "1.5rem"
    xl: str = "2rem"
    xxl: str = "3rem"


@dataclass
class ThemeRadius:
    """Border radius scale"""
    none: str = "0"
    sm: str = "0.25rem"
    md: str = "0.375rem"
    lg: str = "0.5rem"
    xl: str = "0.75rem"
    full: str = "9999px"


@dataclass
class ThemeShadows:
    """Box shadow presets"""
    none: str = "none"
    sm: str = "0 1px 2px 0 rgb(0 0 0 / 0.05)"
    md: str = "0 4px 6px -1px rgb(0 0 0 / 0.1)"
    lg: str = "0 10px 15px -3px rgb(0 0 0 / 0.1)"
    xl: str = "0 20px 25px -5px rgb(0 0 0 / 0.1)"


@dataclass
class Theme:
    """Complete theme configuration"""
    name: str = "light"
    colors: ThemeColors = field(default_factory=ThemeColors)
    spacing: ThemeSpacing = field(default_factory=ThemeSpacing)
    radius: ThemeRadius = field(default_factory=ThemeRadius)
    shadows: ThemeShadows = field(default_factory=ThemeShadows)
    font_family: str = "Inter, system-ui, sans-serif"
    
    def to_css_vars(self) -> str:
        """Generate CSS custom properties"""
        vars = []
        
        # Colors
        for name, value in vars(self.colors).items():
            css_name = name.replace("_", "-")
            vars.append(f"--{css_name}: {value};")
        
        # Spacing
        for name, value in vars(self.spacing).items():
            vars.append(f"--spacing-{name}: {value};")
        
        # Radius
        for name, value in vars(self.radius).items():
            vars.append(f"--radius-{name}: {value};")
        
        # Shadows
        for name, value in vars(self.shadows).items():
            vars.append(f"--shadow-{name}: {value};")
        
        vars.append(f"--font-family: {self.font_family};")
        
        return "\n    ".join(vars)


# Pre-built themes
class Themes:
    """Collection of pre-built themes"""
    
    @staticmethod
    def light() -> Theme:
        return Theme(name="light")
    
    @staticmethod
    def dark() -> Theme:
        return Theme(
            name="dark",
            colors=ThemeColors(
                background="#0f172a",
                foreground="#f8fafc",
                card="#1e293b",
                card_foreground="#f8fafc",
                muted="#334155",
                muted_foreground="#94a3b8",
                border="#334155",
                input="#334155",
            )
        )
    
    @staticmethod
    def midnight() -> Theme:
        return Theme(
            name="midnight",
            colors=ThemeColors(
                primary="#8b5cf6",  # Purple
                secondary="#ec4899",  # Pink
                background="#020617",
                foreground="#f8fafc",
                card="#0f172a",
                card_foreground="#f8fafc",
                muted="#1e293b",
                muted_foreground="#94a3b8",
                border="#1e293b",
            )
        )
    
    @staticmethod
    def forest() -> Theme:
        return Theme(
            name="forest",
            colors=ThemeColors(
                primary="#22c55e",  # Green
                secondary="#14b8a6",  # Teal
                accent="#eab308",  # Yellow
            )
        )


class ThemeProvider:
    """
    Global theme manager.
    
    Usage:
        from pyx import theme
        
        # Set theme
        theme.use(Themes.dark())
        
        # Toggle dark mode
        theme.toggle_dark_mode()
        
        # Get current theme CSS
        theme.get_css()
        
        # Set custom design tokens
        theme.set(primary="#ff5722", radius_md="1rem")
        
        # Extend existing theme
        theme.extend(Themes.dark(), primary="#8b5cf6")
    """
    
    _current: Theme = None
    _dark_mode: bool = False
    _custom_tokens: Dict[str, str] = {}
    
    @classmethod
    def use(cls, theme: Theme):
        """Set the current theme"""
        cls._current = theme
        cls._dark_mode = theme.name in ["dark", "midnight"]
    
    @classmethod
    def get(cls) -> Theme:
        """Get the current theme"""
        if cls._current is None:
            cls._current = Themes.light()
        return cls._current
    
    @classmethod
    def set(cls, **tokens):
        """
        Set custom design tokens.
        
        Usage:
            theme.set(
                primary="#ff5722",
                secondary="#2196f3",
                radius_md="1rem",
                shadow_lg="0 25px 50px -12px rgba(0,0,0,0.25)"
            )
        """
        cls._custom_tokens.update(tokens)
    
    @classmethod
    def extend(cls, base_theme: Theme, **overrides) -> Theme:
        """
        Create a new theme by extending an existing one.
        
        Usage:
            my_theme = theme.extend(
                Themes.dark(),
                primary="#8b5cf6",
                secondary="#ec4899"
            )
            theme.use(my_theme)
        """
        # Create new colors with overrides
        colors_dict = {}
        for key, val in vars(base_theme.colors).items():
            colors_dict[key] = overrides.get(key, val)
        
        new_colors = ThemeColors(**colors_dict)
        
        return Theme(
            name=overrides.get("name", base_theme.name + "-custom"),
            colors=new_colors,
            spacing=base_theme.spacing,
            radius=base_theme.radius,
            shadows=base_theme.shadows,
            font_family=overrides.get("font_family", base_theme.font_family)
        )
    
    @classmethod
    def toggle_dark_mode(cls):
        """Toggle between light and dark mode"""
        cls._dark_mode = not cls._dark_mode
        if cls._dark_mode:
            cls.use(Themes.dark())
        else:
            cls.use(Themes.light())
    
    @classmethod
    def is_dark(cls) -> bool:
        """Check if dark mode is enabled"""
        return cls._dark_mode
    
    @classmethod
    def get_tokens(cls) -> Dict[str, str]:
        """Get all design tokens as dict"""
        theme = cls.get()
        tokens = {}
        
        # Colors
        for name, value in vars(theme.colors).items():
            tokens[name.replace("_", "-")] = value
        
        # Spacing
        for name, value in vars(theme.spacing).items():
            tokens[f"spacing-{name}"] = value
        
        # Radius
        for name, value in vars(theme.radius).items():
            tokens[f"radius-{name}"] = value
        
        # Shadows
        for name, value in vars(theme.shadows).items():
            tokens[f"shadow-{name}"] = value
        
        tokens["font-family"] = theme.font_family
        
        # Apply custom overrides
        for key, val in cls._custom_tokens.items():
            css_key = key.replace("_", "-")
            tokens[css_key] = val
        
        return tokens
    
    @classmethod
    def get_css(cls) -> str:
        """Generate CSS for the current theme"""
        theme = cls.get()
        
        return f"""
        <style id="pyx-theme">
            :root {{
                {theme.to_css_vars()}
            }}
            
            body {{
                font-family: var(--font-family);
                background-color: var(--background);
                color: var(--foreground);
            }}
            
            /* Component styles using CSS vars */
            .pyx-card {{
                background-color: var(--card);
                color: var(--card-foreground);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-md);
            }}
            
            .pyx-input {{
                background-color: var(--input);
                border-color: var(--border);
                border-radius: var(--radius-md);
            }}
            
            .pyx-input:focus {{
                ring-color: var(--ring);
            }}
            
            .pyx-button-primary {{
                background-color: var(--primary);
                color: white;
            }}
            
            .pyx-button-secondary {{
                background-color: var(--secondary);
                color: white;
            }}
            
            .pyx-muted {{
                color: var(--muted-foreground);
            }}
        </style>
        """
    
    @classmethod
    def dark_mode_script(cls) -> str:
        """Generate JS for dark mode toggle"""
        return """
        <script>
            window.PyxTheme = {
                isDark: false,
                
                init: function() {
                    // Check system preference
                    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
                        this.setDark(true);
                    }
                    
                    // Check localStorage
                    const saved = localStorage.getItem('pyx-dark-mode');
                    if (saved !== null) {
                        this.setDark(saved === 'true');
                    }
                },
                
                toggle: function() {
                    this.setDark(!this.isDark);
                },
                
                setDark: function(dark) {
                    this.isDark = dark;
                    document.documentElement.classList.toggle('dark', dark);
                    localStorage.setItem('pyx-dark-mode', dark);
                    
                    // Notify server (optional)
                    if (window.ws && window.ws.readyState === WebSocket.OPEN) {
                        window.ws.send(JSON.stringify({
                            type: 'theme_change',
                            dark: dark
                        }));
                    }
                }
            };
            
            PyxTheme.init();
        </script>
        """


# Global instance
theme = ThemeProvider


class DarkModeToggle:
    """
    Pre-built dark mode toggle button.
    
    Usage:
        DarkModeToggle()
    """
    
    def render(self) -> str:
        return """
        <button onclick="PyxTheme.toggle()" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
            <svg class="w-5 h-5 hidden dark:block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
            </svg>
            <svg class="w-5 h-5 block dark:hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
            </svg>
        </button>
        """
    
    def __str__(self):
        return self.render()
