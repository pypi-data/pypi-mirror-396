"""
PyX Dashboard & Enterprise Components
Pre-built components for business applications.
"""
from typing import List, Dict, Any, Optional, Callable
import uuid


class StatCard:
    """
    Statistics/Metric card for dashboards.
    
    Usage:
        StatCard(
            title="Revenue",
            value="$12,450",
            change="+12%",
            trend="up",
            icon="dollar-sign"
        )
    """
    
    def __init__(
        self,
        title: str,
        value: str,
        change: str = None,
        trend: str = None,  # 'up', 'down', 'neutral'
        icon: str = None,
        description: str = None,
        className: str = "",
    ):
        self.title = title
        self.value = value
        self.change = change
        self.trend = trend
        self.icon = icon
        self.description = description
        self.className = className
    
    def render(self) -> str:
        # Trend colors
        trend_colors = {
            "up": "text-green-600",
            "down": "text-red-600",
            "neutral": "text-gray-500",
        }
        trend_icons = {
            "up": "↑",
            "down": "↓",
            "neutral": "→",
        }
        
        trend_color = trend_colors.get(self.trend, "text-gray-500")
        trend_icon = trend_icons.get(self.trend, "")
        
        change_html = ""
        if self.change:
            change_html = f'<span class="{trend_color} text-sm font-medium">{trend_icon} {self.change}</span>'
        
        icon_html = ""
        if self.icon:
            icon_html = f'<i data-lucide="{self.icon}" class="w-8 h-8 text-gray-400"></i>'
        
        desc_html = ""
        if self.description:
            desc_html = f'<p class="text-xs text-gray-500 mt-1">{self.description}</p>'
        
        return f"""
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 {self.className}">
            <div class="flex justify-between items-start">
                <div>
                    <p class="text-sm font-medium text-gray-500">{self.title}</p>
                    <p class="text-2xl font-bold text-gray-900 mt-1">{self.value}</p>
                    {change_html}
                    {desc_html}
                </div>
                {icon_html}
            </div>
        </div>
        """
    
    def __str__(self):
        return self.render()


class Timeline:
    """
    Timeline/Activity feed component.
    
    Usage:
        Timeline([
            {"title": "Order placed", "time": "2 hours ago", "icon": "shopping-cart"},
            {"title": "Payment received", "time": "1 hour ago", "icon": "credit-card"},
            {"title": "Shipped", "time": "30 min ago", "icon": "truck", "active": True},
        ])
    """
    
    def __init__(
        self,
        items: List[Dict[str, Any]],
        variant: str = "default",  # 'default', 'compact', 'alternate'
        className: str = "",
    ):
        self.items = items
        self.variant = variant
        self.className = className
    
    def render(self) -> str:
        items_html = []
        
        for i, item in enumerate(self.items):
            is_last = i == len(self.items) - 1
            is_active = item.get("active", False)
            
            # Icon or dot
            icon = item.get("icon")
            if icon:
                marker = f'<i data-lucide="{icon}" class="w-4 h-4"></i>'
            else:
                marker = ""
            
            dot_class = "bg-blue-600" if is_active else "bg-gray-300"
            line_class = "" if is_last else "after:absolute after:top-5 after:left-[9px] after:w-0.5 after:h-full after:bg-gray-200"
            
            content = item.get("content", "")
            content_html = content.render() if hasattr(content, 'render') else str(content) if content else ""
            
            items_html.append(f"""
                <div class="relative pl-8 pb-6 {line_class}">
                    <div class="absolute left-0 top-1 w-5 h-5 rounded-full {dot_class} flex items-center justify-center text-white">
                        {marker}
                    </div>
                    <div class="flex flex-col">
                        <span class="font-medium text-gray-900">{item.get('title', '')}</span>
                        <span class="text-sm text-gray-500">{item.get('time', '')}</span>
                        {f'<div class="mt-2">{content_html}</div>' if content_html else ''}
                    </div>
                </div>
            """)
        
        return f'<div class="pyx-timeline {self.className}">{"".join(items_html)}</div>'
    
    def __str__(self):
        return self.render()


class Stepper:
    """
    Multi-step wizard/stepper component.
    
    Usage:
        Stepper(
            steps=["Account", "Profile", "Payment", "Done"],
            current=2
        )
    """
    
    def __init__(
        self,
        steps: List[str],
        current: int = 0,
        variant: str = "default",  # 'default', 'dots', 'numbered'
        on_step_click: Callable = None,
        className: str = "",
    ):
        self.steps = steps
        self.current = current
        self.variant = variant
        self.on_step_click = on_step_click
        self.className = className
        self._id = f"stepper-{uuid.uuid4().hex[:8]}"
    
    def render(self) -> str:
        steps_html = []
        
        for i, step in enumerate(self.steps):
            is_completed = i < self.current
            is_current = i == self.current
            is_future = i > self.current
            
            # Colors
            if is_completed:
                circle_class = "bg-green-600 text-white"
                text_class = "text-green-600"
                line_class = "bg-green-600"
            elif is_current:
                circle_class = "bg-blue-600 text-white"
                text_class = "text-blue-600 font-semibold"
                line_class = "bg-gray-200"
            else:
                circle_class = "bg-gray-200 text-gray-500"
                text_class = "text-gray-400"
                line_class = "bg-gray-200"
            
            # Marker content
            if is_completed:
                marker = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>'
            else:
                marker = str(i + 1)
            
            # Line (except for last step)
            line_html = ""
            if i < len(self.steps) - 1:
                line_html = f'<div class="flex-1 h-0.5 {line_class} mx-2"></div>'
            
            steps_html.append(f"""
                <div class="flex items-center {'flex-1' if i < len(self.steps) - 1 else ''}">
                    <div class="flex flex-col items-center">
                        <div class="w-8 h-8 rounded-full {circle_class} flex items-center justify-center text-sm font-medium">
                            {marker}
                        </div>
                        <span class="text-xs mt-1 {text_class}">{step}</span>
                    </div>
                    {line_html}
                </div>
            """)
        
        return f'<div class="flex items-center w-full {self.className}">{"".join(steps_html)}</div>'
    
    def __str__(self):
        return self.render()


class Alert:
    """
    Alert/Callout component.
    
    Usage:
        Alert("Operation successful!", variant="success")
        Alert("Warning: Low disk space", variant="warning", dismissible=True)
    """
    
    ICONS = {
        "info": "info",
        "success": "check-circle",
        "warning": "alert-triangle",
        "error": "x-circle",
    }
    
    COLORS = {
        "info": {"bg": "bg-blue-50", "border": "border-blue-200", "text": "text-blue-800", "icon": "text-blue-600"},
        "success": {"bg": "bg-green-50", "border": "border-green-200", "text": "text-green-800", "icon": "text-green-600"},
        "warning": {"bg": "bg-yellow-50", "border": "border-yellow-200", "text": "text-yellow-800", "icon": "text-yellow-600"},
        "error": {"bg": "bg-red-50", "border": "border-red-200", "text": "text-red-800", "icon": "text-red-600"},
    }
    
    def __init__(
        self,
        message: str,
        title: str = None,
        variant: str = "info",  # 'info', 'success', 'warning', 'error'
        dismissible: bool = False,
        icon: str = None,
        className: str = "",
    ):
        self.message = message
        self.title = title
        self.variant = variant
        self.dismissible = dismissible
        self.icon = icon or self.ICONS.get(variant, "info")
        self.className = className
        self._id = f"alert-{uuid.uuid4().hex[:8]}"
    
    def render(self) -> str:
        colors = self.COLORS.get(self.variant, self.COLORS["info"])
        
        title_html = ""
        if self.title:
            title_html = f'<p class="font-semibold">{self.title}</p>'
        
        dismiss_html = ""
        if self.dismissible:
            dismiss_html = f"""
                <button onclick="document.getElementById('{self._id}').remove()" class="ml-auto">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                </button>
            """
        
        return f"""
        <div id="{self._id}" class="flex items-start gap-3 p-4 rounded-lg border {colors['bg']} {colors['border']} {colors['text']} {self.className}">
            <i data-lucide="{self.icon}" class="w-5 h-5 {colors['icon']} flex-shrink-0 mt-0.5"></i>
            <div class="flex-1">
                {title_html}
                <p class="text-sm">{self.message}</p>
            </div>
            {dismiss_html}
        </div>
        """
    
    def __str__(self):
        return self.render()


class EmptyState:
    """
    Empty state placeholder.
    
    Usage:
        EmptyState(
            title="No results found",
            description="Try adjusting your search",
            icon="search",
            action=ui.button("Clear filters")
        )
    """
    
    def __init__(
        self,
        title: str,
        description: str = None,
        icon: str = "inbox",
        action=None,
        className: str = "",
    ):
        self.title = title
        self.description = description
        self.icon = icon
        self.action = action
        self.className = className
    
    def render(self) -> str:
        desc_html = f'<p class="text-gray-500 mt-1">{self.description}</p>' if self.description else ""
        
        action_html = ""
        if self.action:
            action_content = self.action.render() if hasattr(self.action, 'render') else str(self.action)
            action_html = f'<div class="mt-4">{action_content}</div>'
        
        return f"""
        <div class="flex flex-col items-center justify-center py-12 text-center {self.className}">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <i data-lucide="{self.icon}" class="w-8 h-8 text-gray-400"></i>
            </div>
            <h3 class="text-lg font-medium text-gray-900">{self.title}</h3>
            {desc_html}
            {action_html}
        </div>
        """
    
    def __str__(self):
        return self.render()


class Avatar:
    """
    Avatar component.
    
    Usage:
        Avatar(src="/avatar.jpg", name="John Doe")
        Avatar(name="JD", size="lg")  # Initials fallback
    """
    
    SIZES = {
        "xs": "w-6 h-6 text-xs",
        "sm": "w-8 h-8 text-sm",
        "md": "w-10 h-10 text-base",
        "lg": "w-12 h-12 text-lg",
        "xl": "w-16 h-16 text-xl",
    }
    
    def __init__(
        self,
        src: str = None,
        name: str = None,
        alt: str = None,
        size: str = "md",
        status: str = None,  # 'online', 'offline', 'busy', 'away'
        className: str = "",
    ):
        self.src = src
        self.name = name
        self.alt = alt or name or ""
        self.size = size
        self.status = status
        self.className = className
    
    def _get_initials(self) -> str:
        if not self.name:
            return "?"
        parts = self.name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        return self.name[:2].upper()
    
    def render(self) -> str:
        size_class = self.SIZES.get(self.size, self.SIZES["md"])
        
        # Status indicator
        status_colors = {
            "online": "bg-green-500",
            "offline": "bg-gray-400",
            "busy": "bg-red-500",
            "away": "bg-yellow-500",
        }
        status_html = ""
        if self.status:
            status_color = status_colors.get(self.status, "bg-gray-400")
            status_html = f'<span class="absolute bottom-0 right-0 w-3 h-3 {status_color} border-2 border-white rounded-full"></span>'
        
        if self.src:
            content = f'<img src="{self.src}" alt="{self.alt}" class="{size_class} rounded-full object-cover">'
        else:
            content = f'<span class="{size_class} rounded-full bg-gray-300 text-gray-700 flex items-center justify-center font-medium">{self._get_initials()}</span>'
        
        return f'<div class="relative inline-block {self.className}">{content}{status_html}</div>'
    
    def __str__(self):
        return self.render()


class AvatarGroup:
    """
    Group of avatars with overlap.
    
    Usage:
        AvatarGroup([
            {"src": "/user1.jpg", "name": "John"},
            {"src": "/user2.jpg", "name": "Jane"},
            {"name": "Bob"},
        ], max=3)
    """
    
    def __init__(
        self,
        avatars: List[Dict[str, Any]],
        max: int = 4,
        size: str = "md",
        className: str = "",
    ):
        self.avatars = avatars
        self.max = max
        self.size = size
        self.className = className
    
    def render(self) -> str:
        visible = self.avatars[:self.max]
        remaining = len(self.avatars) - self.max
        
        avatars_html = []
        for i, avatar_data in enumerate(visible):
            avatar = Avatar(
                src=avatar_data.get("src"),
                name=avatar_data.get("name"),
                size=self.size,
                className=f"-ml-2 first:ml-0 ring-2 ring-white"
            )
            avatars_html.append(avatar.render())
        
        # +N indicator
        extra_html = ""
        if remaining > 0:
            size_class = Avatar.SIZES.get(self.size, Avatar.SIZES["md"])
            extra_html = f'<span class="{size_class} -ml-2 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center font-medium ring-2 ring-white">+{remaining}</span>'
        
        return f'<div class="flex items-center {self.className}">{"".join(avatars_html)}{extra_html}</div>'
    
    def __str__(self):
        return self.render()


class Breadcrumb:
    """
    Breadcrumb navigation.
    
    Usage:
        Breadcrumb([
            {"label": "Home", "href": "/"},
            {"label": "Products", "href": "/products"},
            {"label": "Electronics"},  # Current (no href)
        ])
    """
    
    def __init__(
        self,
        items: List[Dict[str, str]],
        separator: str = "/",
        className: str = "",
    ):
        self.items = items
        self.separator = separator
        self.className = className
    
    def render(self) -> str:
        items_html = []
        
        for i, item in enumerate(self.items):
            is_last = i == len(self.items) - 1
            
            if is_last or not item.get("href"):
                # Current/active item
                items_html.append(f'<span class="text-gray-800 font-medium">{item["label"]}</span>')
            else:
                items_html.append(f'<a href="{item["href"]}" class="text-gray-500 hover:text-gray-700">{item["label"]}</a>')
            
            if not is_last:
                items_html.append(f'<span class="text-gray-400 mx-2">{self.separator}</span>')
        
        return f'<nav class="flex items-center text-sm {self.className}">{"".join(items_html)}</nav>'
    
    def __str__(self):
        return self.render()
