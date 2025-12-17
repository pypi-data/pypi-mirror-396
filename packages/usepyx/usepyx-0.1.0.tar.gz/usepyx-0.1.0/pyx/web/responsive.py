"""
PyX Responsive Utilities
Make responsive design easier with Pythonic API.
"""
from typing import Dict, Any, Union, List
from dataclasses import dataclass


# Tailwind breakpoints
BREAKPOINTS = {
    "sm": 640,    # Small tablets
    "md": 768,    # Tablets
    "lg": 1024,   # Laptops
    "xl": 1280,   # Desktops
    "2xl": 1536,  # Large screens
}


@dataclass
class Breakpoint:
    """Responsive breakpoint values"""
    mobile: Any = None   # Default (no prefix)
    sm: Any = None       # >= 640px
    md: Any = None       # >= 768px
    lg: Any = None       # >= 1024px
    xl: Any = None       # >= 1280px
    xxl: Any = None      # >= 1536px


class Responsive:
    """
    Responsive design utilities for PyX.
    
    Usage:
        from pyx import responsive as r
        
        # Responsive classes
        r.text("sm", "md:base", "lg:lg")  # text-sm md:text-base lg:text-lg
        r.grid(1, md=2, lg=4)              # grid-cols-1 md:grid-cols-2 lg:grid-cols-4
        r.hide(on="mobile")                # hidden md:block
        r.show(on="mobile")                # md:hidden
        
        # Responsive spacing
        r.padding(2, md=4, lg=6)           # p-2 md:p-4 lg:p-6
        r.margin(1, md=2, lg=4)            # m-1 md:m-2 lg:m-4
    """
    
    @staticmethod
    def cls(
        mobile: str = "",
        sm: str = None,
        md: str = None,
        lg: str = None,
        xl: str = None,
        xxl: str = None
    ) -> str:
        """
        Build responsive class string.
        
        Usage:
            responsive.cls("text-sm", md="text-base", lg="text-lg")
            # Returns: "text-sm md:text-base lg:text-lg"
        """
        classes = [mobile] if mobile else []
        
        if sm:
            classes.append(f"sm:{sm}")
        if md:
            classes.append(f"md:{md}")
        if lg:
            classes.append(f"lg:{lg}")
        if xl:
            classes.append(f"xl:{xl}")
        if xxl:
            classes.append(f"2xl:{xxl}")
        
        return " ".join(classes)
    
    @staticmethod
    def grid(
        cols: int = 1,
        sm: int = None,
        md: int = None,
        lg: int = None,
        xl: int = None,
        gap: int = 4
    ) -> str:
        """
        Responsive grid columns.
        
        Usage:
            responsive.grid(1, md=2, lg=3, xl=4)
            # Returns: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
        """
        classes = [f"grid grid-cols-{cols}"]
        
        if sm:
            classes.append(f"sm:grid-cols-{sm}")
        if md:
            classes.append(f"md:grid-cols-{md}")
        if lg:
            classes.append(f"lg:grid-cols-{lg}")
        if xl:
            classes.append(f"xl:grid-cols-{xl}")
        
        classes.append(f"gap-{gap}")
        
        return " ".join(classes)
    
    @staticmethod
    def flex(
        direction: str = "col",  # "row", "col"
        sm: str = None,
        md: str = None,
        lg: str = None,
        gap: int = 4
    ) -> str:
        """
        Responsive flex direction.
        
        Usage:
            responsive.flex("col", md="row")
            # Stack on mobile, row on desktop
        """
        classes = [f"flex flex-{direction}"]
        
        if sm:
            classes.append(f"sm:flex-{sm}")
        if md:
            classes.append(f"md:flex-{md}")
        if lg:
            classes.append(f"lg:flex-{lg}")
        
        classes.append(f"gap-{gap}")
        
        return " ".join(classes)
    
    @staticmethod
    def text(
        size: str = "sm",
        sm: str = None,
        md: str = None,
        lg: str = None,
        xl: str = None
    ) -> str:
        """
        Responsive text size.
        
        Usage:
            responsive.text("sm", md="base", lg="lg", xl="xl")
        """
        classes = [f"text-{size}"]
        
        if sm:
            classes.append(f"sm:text-{sm}")
        if md:
            classes.append(f"md:text-{md}")
        if lg:
            classes.append(f"lg:text-{lg}")
        if xl:
            classes.append(f"xl:text-{xl}")
        
        return " ".join(classes)
    
    @staticmethod
    def padding(
        size: int = 4,
        sm: int = None,
        md: int = None,
        lg: int = None,
        xl: int = None,
        x: int = None,
        y: int = None
    ) -> str:
        """
        Responsive padding.
        
        Usage:
            responsive.padding(2, md=4, lg=6)
            responsive.padding(x=4, y=2)
        """
        if x is not None or y is not None:
            classes = []
            if x is not None:
                classes.append(f"px-{x}")
            if y is not None:
                classes.append(f"py-{y}")
            return " ".join(classes)
        
        classes = [f"p-{size}"]
        
        if sm:
            classes.append(f"sm:p-{sm}")
        if md:
            classes.append(f"md:p-{md}")
        if lg:
            classes.append(f"lg:p-{lg}")
        if xl:
            classes.append(f"xl:p-{xl}")
        
        return " ".join(classes)
    
    @staticmethod
    def margin(
        size: int = 4,
        sm: int = None,
        md: int = None,
        lg: int = None,
        xl: int = None
    ) -> str:
        """
        Responsive margin.
        
        Usage:
            responsive.margin(2, md=4, lg=6)
        """
        classes = [f"m-{size}"]
        
        if sm:
            classes.append(f"sm:m-{sm}")
        if md:
            classes.append(f"md:m-{md}")
        if lg:
            classes.append(f"lg:m-{lg}")
        if xl:
            classes.append(f"xl:m-{xl}")
        
        return " ".join(classes)
    
    @staticmethod
    def width(
        size: str = "full",
        sm: str = None,
        md: str = None,
        lg: str = None,
        xl: str = None
    ) -> str:
        """
        Responsive width.
        
        Usage:
            responsive.width("full", md="1/2", lg="1/3")
        """
        classes = [f"w-{size}"]
        
        if sm:
            classes.append(f"sm:w-{sm}")
        if md:
            classes.append(f"md:w-{md}")
        if lg:
            classes.append(f"lg:w-{lg}")
        if xl:
            classes.append(f"xl:w-{xl}")
        
        return " ".join(classes)
    
    @staticmethod
    def hide(on: str = "mobile") -> str:
        """
        Hide element on specific breakpoint.
        
        Usage:
            responsive.hide(on="mobile")  # Hidden on mobile, visible on md+
            responsive.hide(on="desktop") # Visible on mobile, hidden on lg+
        """
        if on == "mobile":
            return "hidden md:block"
        elif on == "tablet":
            return "hidden lg:block"
        elif on == "desktop":
            return "lg:hidden"
        elif on == "lg":
            return "lg:hidden"
        elif on == "md":
            return "md:hidden"
        return "hidden"
    
    @staticmethod
    def show(on: str = "mobile") -> str:
        """
        Show element only on specific breakpoint.
        
        Usage:
            responsive.show(on="mobile")  # Visible only on mobile
            responsive.show(on="desktop") # Visible only on desktop
        """
        if on == "mobile":
            return "block md:hidden"
        elif on == "tablet":
            return "hidden md:block lg:hidden"
        elif on == "desktop":
            return "hidden lg:block"
        return "block"
    
    @staticmethod
    def container(padding: bool = True, center: bool = True) -> str:
        """
        Responsive container classes.
        
        Usage:
            responsive.container()
            # "container mx-auto px-4 md:px-6 lg:px-8"
        """
        classes = ["container"]
        
        if center:
            classes.append("mx-auto")
        
        if padding:
            classes.append("px-4 md:px-6 lg:px-8")
        
        return " ".join(classes)
    
    @staticmethod
    def stack(gap: int = 4, md_gap: int = None, lg_gap: int = None) -> str:
        """
        Responsive vertical stack.
        
        Usage:
            responsive.stack(4, md_gap=6, lg_gap=8)
        """
        classes = [f"flex flex-col gap-{gap}"]
        
        if md_gap:
            classes.append(f"md:gap-{md_gap}")
        if lg_gap:
            classes.append(f"lg:gap-{lg_gap}")
        
        return " ".join(classes)
    
    @staticmethod  
    def hstack(gap: int = 4, wrap: bool = True, md_gap: int = None) -> str:
        """
        Responsive horizontal stack.
        
        Usage:
            responsive.hstack(4, wrap=True)
        """
        classes = [f"flex flex-row gap-{gap}"]
        
        if wrap:
            classes.append("flex-wrap")
        
        if md_gap:
            classes.append(f"md:gap-{md_gap}")
        
        return " ".join(classes)


# Singleton instance
responsive = Responsive()


class Show:
    """
    Conditional rendering based on breakpoint.
    
    Usage:
        Show.on_mobile(
            ui.div("Mobile menu")
        )
        
        Show.on_desktop(
            ui.div("Desktop sidebar")
        )
    """
    
    @staticmethod
    def on_mobile(content) -> str:
        """Show only on mobile (< 768px)"""
        html = content.render() if hasattr(content, 'render') else str(content)
        return f'<div class="block md:hidden">{html}</div>'
    
    @staticmethod
    def on_tablet(content) -> str:
        """Show only on tablet (768px - 1024px)"""
        html = content.render() if hasattr(content, 'render') else str(content)
        return f'<div class="hidden md:block lg:hidden">{html}</div>'
    
    @staticmethod
    def on_desktop(content) -> str:
        """Show only on desktop (>= 1024px)"""
        html = content.render() if hasattr(content, 'render') else str(content)
        return f'<div class="hidden lg:block">{html}</div>'
    
    @staticmethod
    def above(breakpoint: str, content) -> str:
        """Show above breakpoint"""
        html = content.render() if hasattr(content, 'render') else str(content)
        return f'<div class="hidden {breakpoint}:block">{html}</div>'
    
    @staticmethod
    def below(breakpoint: str, content) -> str:
        """Show below breakpoint"""
        html = content.render() if hasattr(content, 'render') else str(content)
        return f'<div class="{breakpoint}:hidden">{html}</div>'


class Hide:
    """
    Hide content based on breakpoint.
    
    Usage:
        Hide.on_mobile(content)
        Hide.on_desktop(content)
    """
    
    @staticmethod
    def on_mobile(content) -> str:
        """Hide on mobile, show on md+"""
        html = content.render() if hasattr(content, 'render') else str(content)
        return f'<div class="hidden md:block">{html}</div>'
    
    @staticmethod
    def on_desktop(content) -> str:
        """Hide on desktop (lg+)"""
        html = content.render() if hasattr(content, 'render') else str(content)
        return f'<div class="lg:hidden">{html}</div>'


class ResponsiveStyles:
    """
    Generate responsive CSS utilities.
    """
    
    @staticmethod
    def viewport_meta() -> str:
        """Essential viewport meta tag"""
        return '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">'
    
    @staticmethod
    def base_styles() -> str:
        """Base responsive styles"""
        return '''
        <style>
            /* Responsive base */
            * { box-sizing: border-box; }
            
            html {
                -webkit-text-size-adjust: 100%;
                text-size-adjust: 100%;
            }
            
            img, video, svg {
                max-width: 100%;
                height: auto;
            }
            
            /* Touch-friendly targets */
            @media (pointer: coarse) {
                button, a, input, select, textarea {
                    min-height: 44px;
                    min-width: 44px;
                }
            }
            
            /* Reduce motion for accessibility */
            @media (prefers-reduced-motion: reduce) {
                *, *::before, *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            }
            
            /* Dark mode support */
            @media (prefers-color-scheme: dark) {
                :root {
                    color-scheme: dark;
                }
            }
        </style>
        '''
