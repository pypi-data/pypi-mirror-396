"""
PyX Animation System
Pre-built animations and transition utilities.
"""
from typing import Optional


class Animate:
    """
    Animation wrapper for elements.
    
    Usage:
        Animate(ui.div("Hello"), animation="fadeIn")
        Animate(ui.card(...), animation="slideUp", delay="0.2s")
    """
    
    # Pre-built animation keyframes
    KEYFRAMES = """
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideLeft {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideRight {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.9); }
        to { opacity: 1; transform: scale(1); }
    }
    
    @keyframes scaleOut {
        from { opacity: 1; transform: scale(1); }
        to { opacity: 0; transform: scale(0.9); }
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    @keyframes ping {
        75%, 100% { transform: scale(2); opacity: 0; }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    """
    
    ANIMATIONS = {
        "fadeIn": "fadeIn 0.3s ease-out forwards",
        "fadeOut": "fadeOut 0.3s ease-out forwards",
        "slideUp": "slideUp 0.4s ease-out forwards",
        "slideDown": "slideDown 0.4s ease-out forwards",
        "slideLeft": "slideLeft 0.4s ease-out forwards",
        "slideRight": "slideRight 0.4s ease-out forwards",
        "scaleIn": "scaleIn 0.3s ease-out forwards",
        "scaleOut": "scaleOut 0.3s ease-out forwards",
        "bounce": "bounce 1s ease-in-out infinite",
        "pulse": "pulse 2s ease-in-out infinite",
        "spin": "spin 1s linear infinite",
        "ping": "ping 1s cubic-bezier(0, 0, 0.2, 1) infinite",
        "shake": "shake 0.5s ease-in-out",
    }
    
    _styles_injected = False
    
    def __init__(
        self,
        child,
        animation: str = "fadeIn",
        duration: str = None,
        delay: str = None,
        easing: str = None,
        iteration: str = None,  # 'infinite' or number
        className: str = "",
    ):
        self.child = child
        self.animation = animation
        self.duration = duration
        self.delay = delay
        self.easing = easing
        self.iteration = iteration
        self.className = className
    
    def render(self) -> str:
        child_html = self.child.render() if hasattr(self.child, 'render') else str(self.child)
        
        # Build animation style
        anim = self.ANIMATIONS.get(self.animation, self.animation)
        
        style_parts = [f"animation: {anim}"]
        if self.duration:
            style_parts.append(f"animation-duration: {self.duration}")
        if self.delay:
            style_parts.append(f"animation-delay: {self.delay}")
        if self.easing:
            style_parts.append(f"animation-timing-function: {self.easing}")
        if self.iteration:
            style_parts.append(f"animation-iteration-count: {self.iteration}")
        
        style = "; ".join(style_parts)
        
        # Inject keyframes once
        keyframes = ""
        if not Animate._styles_injected:
            keyframes = f"<style>{self.KEYFRAMES}</style>"
            Animate._styles_injected = True
        
        return f'{keyframes}<div class="{self.className}" style="{style}">{child_html}</div>'
    
    def __str__(self):
        return self.render()


class Transition:
    """
    Add CSS transitions to elements.
    
    Usage:
        Transition(ui.button("Hover me"), property="all", duration="0.3s")
    """
    
    PRESETS = {
        "default": "all 0.2s ease",
        "fast": "all 0.1s ease",
        "slow": "all 0.5s ease",
        "colors": "color, background-color, border-color 0.2s ease",
        "opacity": "opacity 0.2s ease",
        "transform": "transform 0.3s ease",
        "shadow": "box-shadow 0.2s ease",
    }
    
    def __init__(
        self,
        child,
        preset: str = "default",
        property: str = None,
        duration: str = None,
        easing: str = None,
        className: str = "",
    ):
        self.child = child
        self.preset = preset
        self.property = property
        self.duration = duration
        self.easing = easing
        self.className = className
    
    def render(self) -> str:
        child_html = self.child.render() if hasattr(self.child, 'render') else str(self.child)
        
        if self.property:
            transition = f"{self.property} {self.duration or '0.2s'} {self.easing or 'ease'}"
        else:
            transition = self.PRESETS.get(self.preset, self.PRESETS["default"])
        
        return f'<div class="{self.className}" style="transition: {transition}">{child_html}</div>'
    
    def __str__(self):
        return self.render()


class Spinner:
    """
    Loading spinner.
    
    Usage:
        Spinner()
        Spinner(size="lg", color="blue")
    """
    
    SIZES = {
        "xs": "w-3 h-3",
        "sm": "w-4 h-4",
        "md": "w-6 h-6",
        "lg": "w-8 h-8",
        "xl": "w-12 h-12",
    }
    
    def __init__(self, size: str = "md", color: str = "blue", className: str = ""):
        self.size = size
        self.color = color
        self.className = className
    
    def render(self) -> str:
        size_class = self.SIZES.get(self.size, self.SIZES["md"])
        
        return f'''
        <svg class="animate-spin {size_class} text-{self.color}-600 {self.className}" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        '''
    
    def __str__(self):
        return self.render()


class Skeleton:
    """
    Skeleton loading animation.
    Already implemented in essential.py, this is an alias.
    """
    pass


# Animation utility functions
def fade_in(child, duration="0.3s", delay=None):
    """Quick fadeIn animation"""
    return Animate(child, animation="fadeIn", duration=duration, delay=delay)

def slide_up(child, duration="0.4s", delay=None):
    """Quick slideUp animation"""
    return Animate(child, animation="slideUp", duration=duration, delay=delay)

def slide_down(child, duration="0.4s", delay=None):
    """Quick slideDown animation"""
    return Animate(child, animation="slideDown", duration=duration, delay=delay)

def scale_in(child, duration="0.3s", delay=None):
    """Quick scaleIn animation"""
    return Animate(child, animation="scaleIn", duration=duration, delay=delay)

def spin(child):
    """Infinite spin animation"""
    return Animate(child, animation="spin")

def pulse(child):
    """Infinite pulse animation"""
    return Animate(child, animation="pulse")

def bounce(child):
    """Infinite bounce animation"""
    return Animate(child, animation="bounce")
