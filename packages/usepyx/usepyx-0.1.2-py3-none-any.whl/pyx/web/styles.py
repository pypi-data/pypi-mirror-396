"""
PyX Pythonic Style System
Style your UI without writing Tailwind classes directly.
"""
from typing import Dict, Any, Union, List, Optional
from dataclasses import dataclass, field


class Style:
    """
    Pythonic style builder - no Tailwind strings needed!
    
    Usage:
        # Instead of:
        ui.div("Hello").cls("text-sm text-red-500 font-bold p-4 bg-white rounded-lg shadow-md")
        
        # Use:
        ui.div("Hello").style(
            text="sm",
            color="red-500",
            font="bold",
            p=4,
            bg="white",
            rounded="lg",
            shadow="md"
        )
        
        # Or with Style class:
        my_style = Style(text="sm", color="red-500", font="bold")
        ui.div("Hello").apply(my_style)
    """
    
    def __init__(self, **kwargs):
        self._classes: List[str] = []
        
        for key, value in kwargs.items():
            self._add_property(key, value)
    
    def _add_property(self, key: str, value: Any):
        """Convert Python property to Tailwind class"""
        
        # Handle None values
        if value is None:
            return
        
        # Handle boolean values
        if isinstance(value, bool):
            if value:
                self._classes.append(key.replace("_", "-"))
            return
        
        # Convert key from snake_case to kebab-case
        key = key.replace("_", "-")
        
        # Special mappings
        mappings = {
            # Typography
            "text": lambda v: f"text-{v}",
            "color": lambda v: f"text-{v}",
            "font": lambda v: f"font-{v}",
            "size": lambda v: f"text-{v}",
            "weight": lambda v: f"font-{v}",
            "leading": lambda v: f"leading-{v}",
            "tracking": lambda v: f"tracking-{v}",
            "align": lambda v: f"text-{v}",
            
            # Spacing
            "p": lambda v: f"p-{v}",
            "px": lambda v: f"px-{v}",
            "py": lambda v: f"py-{v}",
            "pt": lambda v: f"pt-{v}",
            "pb": lambda v: f"pb-{v}",
            "pl": lambda v: f"pl-{v}",
            "pr": lambda v: f"pr-{v}",
            "m": lambda v: f"m-{v}",
            "mx": lambda v: f"mx-{v}",
            "my": lambda v: f"my-{v}",
            "mt": lambda v: f"mt-{v}",
            "mb": lambda v: f"mb-{v}",
            "ml": lambda v: f"ml-{v}",
            "mr": lambda v: f"mr-{v}",
            "gap": lambda v: f"gap-{v}",
            "space-x": lambda v: f"space-x-{v}",
            "space-y": lambda v: f"space-y-{v}",
            
            # Sizing
            "w": lambda v: f"w-{v}",
            "h": lambda v: f"h-{v}",
            "min-w": lambda v: f"min-w-{v}",
            "min-h": lambda v: f"min-h-{v}",
            "max-w": lambda v: f"max-w-{v}",
            "max-h": lambda v: f"max-h-{v}",
            
            # Background
            "bg": lambda v: f"bg-{v}",
            
            # Border
            "border": lambda v: f"border-{v}" if v != True else "border",
            "border-t": lambda v: f"border-t-{v}",
            "border-b": lambda v: f"border-b-{v}",
            "border-l": lambda v: f"border-l-{v}",
            "border-r": lambda v: f"border-r-{v}",
            "rounded": lambda v: f"rounded-{v}" if v != "full" else "rounded-full",
            
            # Effects
            "shadow": lambda v: f"shadow-{v}" if v != True else "shadow",
            "opacity": lambda v: f"opacity-{v}",
            "blur": lambda v: f"blur-{v}" if v else "blur",
            
            # Layout
            "flex": lambda v: "flex" if v == True else f"flex-{v}",
            "grid": lambda v: "grid" if v == True else f"grid-cols-{v}",
            "cols": lambda v: f"grid-cols-{v}",
            "rows": lambda v: f"grid-rows-{v}",
            "justify": lambda v: f"justify-{v}",
            "items": lambda v: f"items-{v}",
            "self": lambda v: f"self-{v}",
            
            # Position
            "position": lambda v: v,  # "relative", "absolute", etc
            "z": lambda v: f"z-{v}",
            "inset": lambda v: f"inset-{v}",
            "top": lambda v: f"top-{v}",
            "bottom": lambda v: f"bottom-{v}",
            "left": lambda v: f"left-{v}",
            "right": lambda v: f"right-{v}",
            
            # Display
            "display": lambda v: v,  # "block", "inline", "hidden", etc
            "overflow": lambda v: f"overflow-{v}",
            "cursor": lambda v: f"cursor-{v}",
            
            # Transitions
            "transition": lambda v: f"transition-{v}" if v != True else "transition",
            "duration": lambda v: f"duration-{v}",
            "ease": lambda v: f"ease-{v}",
            
            # Transforms
            "scale": lambda v: f"scale-{v}",
            "rotate": lambda v: f"rotate-{v}",
            "translate-x": lambda v: f"translate-x-{v}",
            "translate-y": lambda v: f"translate-y-{v}",
        }
        
        if key in mappings:
            self._classes.append(mappings[key](value))
        else:
            # Direct class
            self._classes.append(f"{key}-{value}" if value != True else key)
    
    def __str__(self) -> str:
        return " ".join(self._classes)
    
    def __add__(self, other: "Style") -> "Style":
        """Combine two styles"""
        new_style = Style()
        new_style._classes = self._classes + other._classes
        return new_style
    
    def to_class(self) -> str:
        """Convert to Tailwind class string"""
        return str(self)


# Pre-built style presets
class Presets:
    """
    Pre-built style combinations.
    
    Usage:
        ui.div("Card Content").apply(presets.card)
        ui.button("Click").apply(presets.button_primary)
    """
    
    # Cards
    card = Style(bg="white", p=6, rounded="xl", shadow="sm", border="gray-200")
    card_dark = Style(bg="gray-800", p=6, rounded="xl", shadow="lg", border="gray-700")
    card_hover = Style(bg="white", p=6, rounded="xl", shadow="sm", border="gray-200", 
                       transition=True, hover_shadow="md")
    
    # Buttons
    button_primary = Style(
        bg="blue-600", color="white", px=4, py=2, rounded="lg",
        font="medium", transition=True
    )
    button_secondary = Style(
        bg="gray-200", color="gray-800", px=4, py=2, rounded="lg",
        font="medium", transition=True
    )
    button_outline = Style(
        border="gray-300", color="gray-700", px=4, py=2, rounded="lg",
        font="medium", bg="transparent", transition=True
    )
    button_ghost = Style(
        color="gray-600", px=4, py=2, rounded="lg",
        font="medium", transition=True
    )
    button_danger = Style(
        bg="red-600", color="white", px=4, py=2, rounded="lg",
        font="medium", transition=True
    )
    
    # Inputs
    input = Style(
        w="full", p=2, border="gray-300", rounded="md",
        bg="white", color="gray-900"
    )
    input_lg = Style(
        w="full", p=3, border="gray-300", rounded="lg",
        bg="white", color="gray-900", text="lg"
    )
    
    # Links
    link = Style(color="blue-600", font="medium")
    link_muted = Style(color="gray-500", font="normal")
    
    # Text
    heading = Style(text="2xl", font="bold", color="gray-900")
    subheading = Style(text="lg", font="semibold", color="gray-700")
    body = Style(text="base", color="gray-600", leading="relaxed")
    caption = Style(text="sm", color="gray-500")
    
    # Containers
    container = Style(max_w="7xl", mx="auto", px=4)
    section = Style(py=12)
    
    # Badges
    badge = Style(px=2, py=1, rounded="full", text="xs", font="medium")
    badge_success = Style(bg="green-100", color="green-800", px=2, py=1, rounded="full", text="xs", font="medium")
    badge_warning = Style(bg="yellow-100", color="yellow-800", px=2, py=1, rounded="full", text="xs", font="medium")
    badge_danger = Style(bg="red-100", color="red-800", px=2, py=1, rounded="full", text="xs", font="medium")
    badge_info = Style(bg="blue-100", color="blue-800", px=2, py=1, rounded="full", text="xs", font="medium")


presets = Presets()


# Responsive style builder
class ResponsiveStyle:
    """
    Build responsive styles.
    
    Usage:
        rs = ResponsiveStyle()
        rs.base(text="sm", p=2)
        rs.md(text="base", p=4)
        rs.lg(text="lg", p=6)
        
        ui.div("Content").cls(rs.build())
    """
    
    def __init__(self):
        self._base: List[str] = []
        self._sm: List[str] = []
        self._md: List[str] = []
        self._lg: List[str] = []
        self._xl: List[str] = []
        self._xxl: List[str] = []
    
    def base(self, **kwargs) -> "ResponsiveStyle":
        """Base styles (mobile first)"""
        self._base.append(str(Style(**kwargs)))
        return self
    
    def sm(self, **kwargs) -> "ResponsiveStyle":
        """Styles for sm breakpoint (640px+)"""
        for key, value in kwargs.items():
            s = Style(**{key: value})
            for cls in str(s).split():
                self._sm.append(f"sm:{cls}")
        return self
    
    def md(self, **kwargs) -> "ResponsiveStyle":
        """Styles for md breakpoint (768px+)"""
        for key, value in kwargs.items():
            s = Style(**{key: value})
            for cls in str(s).split():
                self._md.append(f"md:{cls}")
        return self
    
    def lg(self, **kwargs) -> "ResponsiveStyle":
        """Styles for lg breakpoint (1024px+)"""
        for key, value in kwargs.items():
            s = Style(**{key: value})
            for cls in str(s).split():
                self._lg.append(f"lg:{cls}")
        return self
    
    def xl(self, **kwargs) -> "ResponsiveStyle":
        """Styles for xl breakpoint (1280px+)"""
        for key, value in kwargs.items():
            s = Style(**{key: value})
            for cls in str(s).split():
                self._xl.append(f"xl:{cls}")
        return self
    
    def xxl(self, **kwargs) -> "ResponsiveStyle":
        """Styles for 2xl breakpoint (1536px+)"""
        for key, value in kwargs.items():
            s = Style(**{key: value})
            for cls in str(s).split():
                self._xxl.append(f"2xl:{cls}")
        return self
    
    def build(self) -> str:
        """Build final class string"""
        all_classes = (
            self._base + self._sm + self._md + 
            self._lg + self._xl + self._xxl
        )
        return " ".join(all_classes)


# Hover/Focus states
class States:
    """
    State-based styles (hover, focus, active).
    
    Usage:
        states = States()
        states.default(bg="white", color="gray-900")
        states.hover(bg="gray-50", color="blue-600")
        states.focus(ring=2, ring_color="blue-500")
        
        ui.button("Click").cls(states.build())
    """
    
    def __init__(self):
        self._default: List[str] = []
        self._hover: List[str] = []
        self._focus: List[str] = []
        self._active: List[str] = []
        self._disabled: List[str] = []
    
    def default(self, **kwargs) -> "States":
        """Default state styles"""
        self._default.append(str(Style(**kwargs)))
        return self
    
    def hover(self, **kwargs) -> "States":
        """Hover state styles"""
        for key, value in kwargs.items():
            s = Style(**{key: value})
            for cls in str(s).split():
                self._hover.append(f"hover:{cls}")
        return self
    
    def focus(self, **kwargs) -> "States":
        """Focus state styles"""
        for key, value in kwargs.items():
            s = Style(**{key: value})
            for cls in str(s).split():
                self._focus.append(f"focus:{cls}")
        return self
    
    def active(self, **kwargs) -> "States":
        """Active state styles"""
        for key, value in kwargs.items():
            s = Style(**{key: value})
            for cls in str(s).split():
                self._active.append(f"active:{cls}")
        return self
    
    def disabled(self, **kwargs) -> "States":
        """Disabled state styles"""
        for key, value in kwargs.items():
            s = Style(**{key: value})
            for cls in str(s).split():
                self._disabled.append(f"disabled:{cls}")
        return self
    
    def build(self) -> str:
        """Build final class string"""
        all_classes = (
            self._default + self._hover + self._focus + 
            self._active + self._disabled
        )
        return " ".join(all_classes)


# Helper function for inline styling
def style(**kwargs) -> str:
    """
    Quick style helper.
    
    Usage:
        ui.div("Hello").cls(style(text="sm", color="red-500", p=4))
    """
    return str(Style(**kwargs))


def sx(**kwargs) -> str:
    """
    Short alias for style().
    
    Usage:
        ui.div("Hello").cls(sx(bg="blue-500", p=4))
    """
    return style(**kwargs)
