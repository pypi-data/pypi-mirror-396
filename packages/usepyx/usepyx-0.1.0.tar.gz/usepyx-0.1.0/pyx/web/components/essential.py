"""
PyX Essential UI Components
Common interactive components.
"""
from typing import List, Dict, Any, Callable, Optional
import uuid


class Tabs:
    """
    Tabbed interface component.
    
    Usage:
        tabs = Tabs(
            tabs=[
                {"id": "home", "label": "Home", "content": ui.div("Home content")},
                {"id": "settings", "label": "Settings", "content": ui.div("Settings content")},
            ],
            default="home"
        )
    """
    
    def __init__(
        self,
        tabs: List[Dict[str, Any]],
        default: str = None,
        on_change: Callable = None,
        variant: str = "underline",  # 'underline', 'pills', 'boxed'
        className: str = "",
    ):
        self.tabs = tabs
        self.default = default or (tabs[0]["id"] if tabs else None)
        self.on_change = on_change
        self.variant = variant
        self.className = className
        self._id = f"tabs-{uuid.uuid4().hex[:8]}"
    
    def render(self) -> str:
        # Tab button styles based on variant
        if self.variant == "pills":
            base_btn = "px-4 py-2 rounded-full text-sm font-medium transition-colors"
            active_btn = "bg-blue-600 text-white"
            inactive_btn = "bg-gray-100 text-gray-600 hover:bg-gray-200"
        elif self.variant == "boxed":
            base_btn = "px-4 py-2 text-sm font-medium border-b-2 transition-colors"
            active_btn = "border-blue-600 text-blue-600 bg-blue-50"
            inactive_btn = "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
        else:  # underline (default)
            base_btn = "px-4 py-2 text-sm font-medium border-b-2 transition-colors"
            active_btn = "border-blue-600 text-blue-600"
            inactive_btn = "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
        
        # Build tab buttons
        tab_buttons = []
        for tab in self.tabs:
            is_active = tab["id"] == self.default
            btn_class = f"{base_btn} {active_btn if is_active else inactive_btn}"
            tab_buttons.append(f"""
                <button 
                    class="{btn_class}" 
                    data-tab="{tab['id']}"
                    onclick="PyxTabs.switch('{self._id}', '{tab['id']}')"
                >
                    {tab.get('label', tab['id'])}
                </button>
            """)
        
        # Build tab panels
        tab_panels = []
        for tab in self.tabs:
            is_active = tab["id"] == self.default
            content = tab.get("content", "")
            content_html = content.render() if hasattr(content, 'render') else str(content)
            display = "" if is_active else "display: none;"
            tab_panels.append(f"""
                <div class="tab-panel" data-panel="{tab['id']}" style="{display}">
                    {content_html}
                </div>
            """)
        
        return f"""
        <div id="{self._id}" class="pyx-tabs {self.className}">
            <div class="tab-list flex gap-2 border-b border-gray-200 mb-4">
                {"".join(tab_buttons)}
            </div>
            <div class="tab-panels">
                {"".join(tab_panels)}
            </div>
        </div>
        
        <script>
            window.PyxTabs = window.PyxTabs || {{
                switch: function(containerId, tabId) {{
                    const container = document.getElementById(containerId);
                    
                    // Update buttons
                    container.querySelectorAll('[data-tab]').forEach(btn => {{
                        const isActive = btn.dataset.tab === tabId;
                        btn.className = btn.className
                            .replace(/border-blue-600|text-blue-600|bg-blue-600|text-white|bg-blue-50/g, '')
                            .replace(/border-transparent|text-gray-500/g, '');
                        if (isActive) {{
                            btn.classList.add('border-blue-600', 'text-blue-600');
                        }} else {{
                            btn.classList.add('border-transparent', 'text-gray-500');
                        }}
                    }});
                    
                    // Update panels
                    container.querySelectorAll('[data-panel]').forEach(panel => {{
                        panel.style.display = panel.dataset.panel === tabId ? '' : 'none';
                    }});
                }}
            }};
        </script>
        """
    
    def __str__(self):
        return self.render()


class Accordion:
    """
    Collapsible accordion component.
    
    Usage:
        accordion = Accordion(
            items=[
                {"title": "Section 1", "content": ui.div("Content 1")},
                {"title": "Section 2", "content": ui.div("Content 2")},
            ],
            multi=False  # Allow multiple open
        )
    """
    
    def __init__(
        self,
        items: List[Dict[str, Any]],
        multi: bool = False,
        default_open: List[int] = None,
        className: str = "",
    ):
        self.items = items
        self.multi = multi
        self.default_open = default_open or []
        self.className = className
        self._id = f"accordion-{uuid.uuid4().hex[:8]}"
    
    def render(self) -> str:
        items_html = []
        
        for i, item in enumerate(self.items):
            is_open = i in self.default_open
            content = item.get("content", "")
            content_html = content.render() if hasattr(content, 'render') else str(content)
            
            icon_rotate = "rotate-180" if is_open else ""
            content_display = "" if is_open else "display: none;"
            
            items_html.append(f"""
                <div class="accordion-item border border-gray-200 rounded-lg mb-2">
                    <button 
                        class="accordion-header w-full flex justify-between items-center p-4 text-left font-medium hover:bg-gray-50"
                        onclick="PyxAccordion.toggle('{self._id}', {i}, {str(self.multi).lower()})"
                    >
                        <span>{item.get('title', f'Item {i+1}')}</span>
                        <svg class="accordion-icon w-5 h-5 transition-transform {icon_rotate}" data-item="{i}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                        </svg>
                    </button>
                    <div class="accordion-content p-4 border-t border-gray-200" data-content="{i}" style="{content_display}">
                        {content_html}
                    </div>
                </div>
            """)
        
        return f"""
        <div id="{self._id}" class="pyx-accordion {self.className}">
            {"".join(items_html)}
        </div>
        
        <script>
            window.PyxAccordion = window.PyxAccordion || {{
                toggle: function(containerId, index, multi) {{
                    const container = document.getElementById(containerId);
                    const content = container.querySelector(`[data-content="${{index}}"]`);
                    const icon = container.querySelector(`[data-item="${{index}}"]`);
                    const isOpen = content.style.display !== 'none';
                    
                    if (!multi) {{
                        // Close all others
                        container.querySelectorAll('[data-content]').forEach(c => c.style.display = 'none');
                        container.querySelectorAll('.accordion-icon').forEach(i => i.classList.remove('rotate-180'));
                    }}
                    
                    // Toggle current
                    content.style.display = isOpen ? 'none' : '';
                    icon.classList.toggle('rotate-180', !isOpen);
                }}
            }};
        </script>
        """
    
    def __str__(self):
        return self.render()


class Progress:
    """
    Progress bar component.
    
    Usage:
        Progress(value=75, max=100)
        Progress(value=progress_var, animated=True)
    """
    
    def __init__(
        self,
        value: int = 0,
        max: int = 100,
        color: str = "blue",
        size: str = "md",  # 'sm', 'md', 'lg'
        animated: bool = False,
        show_label: bool = False,
        className: str = "",
    ):
        self.value = value
        self.max = max
        self.color = color
        self.size = size
        self.animated = animated
        self.show_label = show_label
        self.className = className
        self._id = f"progress-{uuid.uuid4().hex[:8]}"
    
    def render(self) -> str:
        percent = min(100, max(0, (self.value / self.max) * 100))
        
        sizes = {"sm": "h-1", "md": "h-2", "lg": "h-4"}
        height = sizes.get(self.size, "h-2")
        
        animation = "animate-pulse" if self.animated else ""
        
        label = f'<span class="text-sm text-gray-600">{int(percent)}%</span>' if self.show_label else ""
        
        return f"""
        <div class="pyx-progress {self.className}">
            {label}
            <div class="w-full bg-gray-200 rounded-full {height} overflow-hidden">
                <div 
                    id="{self._id}"
                    class="bg-{self.color}-600 {height} rounded-full transition-all duration-300 {animation}"
                    style="width: {percent}%"
                ></div>
            </div>
        </div>
        """
    
    def __str__(self):
        return self.render()


class Skeleton:
    """
    Skeleton loading placeholder.
    
    Usage:
        Skeleton(width="100%", height="20px")
        Skeleton.text()  # Text line placeholder
        Skeleton.avatar()  # Circular avatar placeholder
        Skeleton.card()  # Card placeholder
    """
    
    def __init__(
        self,
        width: str = "100%",
        height: str = "20px",
        rounded: str = "md",
        className: str = "",
    ):
        self.width = width
        self.height = height
        self.rounded = rounded
        self.className = className
    
    def render(self) -> str:
        return f"""
        <div 
            class="animate-pulse bg-gray-200 rounded-{self.rounded} {self.className}"
            style="width: {self.width}; height: {self.height};"
        ></div>
        """
    
    def __str__(self):
        return self.render()
    
    @staticmethod
    def text(lines: int = 3, className: str = "") -> str:
        """Generate text skeleton lines"""
        lines_html = []
        for i in range(lines):
            width = "100%" if i < lines - 1 else "60%"
            lines_html.append(f'<div class="animate-pulse bg-gray-200 h-4 rounded mb-2" style="width: {width}"></div>')
        return f'<div class="{className}">{"".join(lines_html)}</div>'
    
    @staticmethod
    def avatar(size: str = "48px", className: str = "") -> str:
        """Generate avatar skeleton"""
        return f'<div class="animate-pulse bg-gray-200 rounded-full {className}" style="width: {size}; height: {size};"></div>'
    
    @staticmethod
    def card(className: str = "") -> str:
        """Generate card skeleton"""
        return f"""
        <div class="animate-pulse p-4 border border-gray-200 rounded-lg {className}">
            <div class="flex items-center gap-4 mb-4">
                <div class="bg-gray-200 rounded-full w-12 h-12"></div>
                <div class="flex-1">
                    <div class="bg-gray-200 h-4 rounded w-1/2 mb-2"></div>
                    <div class="bg-gray-200 h-3 rounded w-1/3"></div>
                </div>
            </div>
            <div class="bg-gray-200 h-4 rounded mb-2"></div>
            <div class="bg-gray-200 h-4 rounded mb-2"></div>
            <div class="bg-gray-200 h-4 rounded w-2/3"></div>
        </div>
        """


class Tooltip:
    """
    Tooltip wrapper component.
    
    Usage:
        Tooltip(
            content=ui.button("Hover me"),
            text="This is a tooltip!"
        )
    """
    
    def __init__(
        self,
        content,
        text: str,
        position: str = "top",  # 'top', 'bottom', 'left', 'right'
        className: str = "",
    ):
        self.content = content
        self.text = text
        self.position = position
        self.className = className
        self._id = f"tooltip-{uuid.uuid4().hex[:8]}"
    
    def render(self) -> str:
        content_html = self.content.render() if hasattr(self.content, 'render') else str(self.content)
        
        # Position classes
        positions = {
            "top": "bottom-full left-1/2 -translate-x-1/2 mb-2",
            "bottom": "top-full left-1/2 -translate-x-1/2 mt-2",
            "left": "right-full top-1/2 -translate-y-1/2 mr-2",
            "right": "left-full top-1/2 -translate-y-1/2 ml-2",
        }
        pos_class = positions.get(self.position, positions["top"])
        
        return f"""
        <div class="relative inline-block group {self.className}">
            {content_html}
            <div class="absolute {pos_class} px-2 py-1 bg-gray-900 text-white text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                {self.text}
            </div>
        </div>
        """
    
    def __str__(self):
        return self.render()


class Badge:
    """
    Badge/Tag component.
    
    Usage:
        Badge("New", color="green")
        Badge("Pending", color="yellow")
    """
    
    def __init__(
        self,
        text: str,
        color: str = "blue",
        variant: str = "solid",  # 'solid', 'outline', 'subtle'
        size: str = "sm",
        className: str = "",
    ):
        self.text = text
        self.color = color
        self.variant = variant
        self.size = size
        self.className = className
    
    def render(self) -> str:
        sizes = {
            "xs": "px-1.5 py-0.5 text-xs",
            "sm": "px-2 py-1 text-xs",
            "md": "px-2.5 py-1 text-sm",
        }
        size_class = sizes.get(self.size, sizes["sm"])
        
        if self.variant == "solid":
            color_class = f"bg-{self.color}-600 text-white"
        elif self.variant == "outline":
            color_class = f"border border-{self.color}-600 text-{self.color}-600"
        else:  # subtle
            color_class = f"bg-{self.color}-100 text-{self.color}-700"
        
        return f'<span class="inline-flex items-center rounded-full font-medium {size_class} {color_class} {self.className}">{self.text}</span>'
    
    def __str__(self):
        return self.render()
