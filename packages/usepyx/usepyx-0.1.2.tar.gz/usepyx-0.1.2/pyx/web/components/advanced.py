"""
PyX Advanced Interactive Components
Modern UI patterns and interactions.
"""
from typing import List, Dict, Any, Optional, Callable
import uuid
import json


class CommandPalette:
    """
    Command Palette (Cmd+K / Ctrl+K) component.
    
    Usage:
        palette = CommandPalette(
            commands=[
                {"id": "home", "label": "Go to Home", "icon": "home", "action": navigate_home},
                {"id": "settings", "label": "Open Settings", "icon": "settings", "shortcut": "⌘S"},
                {"id": "logout", "label": "Logout", "icon": "log-out"},
            ],
            placeholder="Type a command...",
        )
    """
    
    def __init__(
        self,
        commands: List[Dict[str, Any]],
        placeholder: str = "Search commands...",
        hotkey: str = "k",  # Trigger key (with Cmd/Ctrl)
        on_select: Callable = None,
        className: str = "",
    ):
        self.commands = commands
        self.placeholder = placeholder
        self.hotkey = hotkey
        self.on_select = on_select
        self.className = className
        self._id = f"cmdpal-{uuid.uuid4().hex[:8]}"
        
    def render(self) -> str:
        # Build command items
        commands_json = json.dumps(self.commands)
        
        # Event handler
        select_handler = ""
        if self.on_select:
            from ..core.events import EventManager
            handler_name = EventManager.register(self.on_select)
            select_handler = f"""
                window.ws.send(JSON.stringify({{
                    type: 'event',
                    handler: '{handler_name}',
                    data: {{ commandId: cmd.id }}
                }}));
            """
        
        return f"""
        <div id="{self._id}" class="command-palette-overlay hidden fixed inset-0 z-50 bg-black/50 flex items-start justify-center pt-[20vh] {self.className}">
            <div class="command-palette bg-white rounded-xl shadow-2xl w-full max-w-lg overflow-hidden">
                <div class="flex items-center border-b px-4">
                    <i data-lucide="search" class="w-5 h-5 text-gray-400"></i>
                    <input 
                        type="text" 
                        id="{self._id}-input"
                        class="flex-1 px-3 py-4 outline-none text-lg"
                        placeholder="{self.placeholder}"
                        oninput="PyxCommandPalette.filter('{self._id}')"
                    >
                    <kbd class="px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded">ESC</kbd>
                </div>
                <div id="{self._id}-results" class="max-h-80 overflow-y-auto p-2">
                    <!-- Results populated by JS -->
                </div>
            </div>
        </div>
        
        <script>
            window.PyxCommandPalette = window.PyxCommandPalette || {{
                commands: {{}},
                
                init: function(id, commands) {{
                    this.commands[id] = commands;
                    this.render(id, commands);
                }},
                
                render: function(id, commands) {{
                    const container = document.getElementById(id + '-results');
                    container.innerHTML = commands.map((cmd, i) => `
                        <div class="command-item flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer hover:bg-gray-100 ${{i === 0 ? 'bg-gray-100' : ''}}" 
                             data-index="${{i}}" onclick="PyxCommandPalette.select('${{id}}', '${{cmd.id}}')">
                            ${{cmd.icon ? `<i data-lucide="${{cmd.icon}}" class="w-5 h-5 text-gray-400"></i>` : ''}}
                            <span class="flex-1">${{cmd.label}}</span>
                            ${{cmd.shortcut ? `<kbd class="px-2 py-1 bg-gray-100 text-gray-400 text-xs rounded">${{cmd.shortcut}}</kbd>` : ''}}
                        </div>
                    `).join('');
                    lucide.createIcons();
                }},
                
                filter: function(id) {{
                    const input = document.getElementById(id + '-input');
                    const query = input.value.toLowerCase();
                    const commands = this.commands[id];
                    const filtered = commands.filter(c => c.label.toLowerCase().includes(query));
                    this.render(id, filtered);
                }},
                
                select: function(id, commandId) {{
                    const cmd = this.commands[id].find(c => c.id === commandId);
                    if (cmd) {{
                        this.close(id);
                        if (cmd.action) {{
                            {select_handler}
                        }}
                    }}
                }},
                
                open: function(id) {{
                    const el = document.getElementById(id);
                    el.classList.remove('hidden');
                    document.getElementById(id + '-input').focus();
                    document.body.style.overflow = 'hidden';
                }},
                
                close: function(id) {{
                    const el = document.getElementById(id);
                    el.classList.add('hidden');
                    document.getElementById(id + '-input').value = '';
                    this.render(id, this.commands[id]);
                    document.body.style.overflow = '';
                }},
                
                toggle: function(id) {{
                    const el = document.getElementById(id);
                    if (el.classList.contains('hidden')) {{
                        this.open(id);
                    }} else {{
                        this.close(id);
                    }}
                }}
            }};
            
            // Initialize
            PyxCommandPalette.init('{self._id}', {commands_json});
            
            // Global hotkey listener
            document.addEventListener('keydown', function(e) {{
                if ((e.metaKey || e.ctrlKey) && e.key === '{self.hotkey}') {{
                    e.preventDefault();
                    PyxCommandPalette.toggle('{self._id}');
                }}
                if (e.key === 'Escape') {{
                    PyxCommandPalette.close('{self._id}');
                }}
            }});
        </script>
        """
    
    def __str__(self):
        return self.render()


class DropdownMenu:
    """
    Dropdown/Context menu component.
    
    Usage:
        DropdownMenu(
            trigger=ui.button("Actions"),
            items=[
                {"label": "Edit", "icon": "edit", "action": handle_edit},
                {"label": "Delete", "icon": "trash-2", "variant": "danger"},
                {"type": "divider"},
                {"label": "More...", "icon": "more-horizontal"},
            ]
        )
    """
    
    def __init__(
        self,
        trigger,
        items: List[Dict[str, Any]],
        position: str = "bottom-left",  # 'bottom-left', 'bottom-right', 'top-left', 'top-right'
        on_select: Callable = None,
        className: str = "",
    ):
        self.trigger = trigger
        self.items = items
        self.position = position
        self.on_select = on_select
        self.className = className
        self._id = f"dropdown-{uuid.uuid4().hex[:8]}"
        
    def render(self) -> str:
        trigger_html = self.trigger.render() if hasattr(self.trigger, 'render') else str(self.trigger)
        
        # Position classes
        pos_classes = {
            "bottom-left": "top-full left-0 mt-1",
            "bottom-right": "top-full right-0 mt-1",
            "top-left": "bottom-full left-0 mb-1",
            "top-right": "bottom-full right-0 mb-1",
        }
        pos_class = pos_classes.get(self.position, pos_classes["bottom-left"])
        
        # Build items
        items_html = []
        for i, item in enumerate(self.items):
            if item.get("type") == "divider":
                items_html.append('<div class="h-px bg-gray-200 my-1"></div>')
            else:
                variant_class = "text-red-600 hover:bg-red-50" if item.get("variant") == "danger" else "hover:bg-gray-100"
                icon_html = f'<i data-lucide="{item["icon"]}" class="w-4 h-4"></i>' if item.get("icon") else ""
                
                items_html.append(f"""
                    <button class="w-full flex items-center gap-2 px-3 py-2 text-sm text-left {variant_class} rounded"
                            onclick="PyxDropdown.close('{self._id}'); {f"PyxDropdown.action('{self._id}', '{item.get('id', i)}')" if item.get('action') else ''}">
                        {icon_html}
                        <span>{item.get('label', '')}</span>
                    </button>
                """)
        
        return f"""
        <div class="relative inline-block {self.className}">
            <div onclick="PyxDropdown.toggle('{self._id}')">
                {trigger_html}
            </div>
            <div id="{self._id}" class="absolute {pos_class} hidden z-40 min-w-48 bg-white rounded-lg shadow-lg border border-gray-200 p-1">
                {"".join(items_html)}
            </div>
        </div>
        
        <script>
            window.PyxDropdown = window.PyxDropdown || {{
                toggle: function(id) {{
                    const el = document.getElementById(id);
                    el.classList.toggle('hidden');
                }},
                close: function(id) {{
                    document.getElementById(id).classList.add('hidden');
                }},
                action: function(id, itemId) {{
                    // Can be extended for callbacks
                }}
            }};
            
            // Close on outside click
            document.addEventListener('click', function(e) {{
                if (!e.target.closest('[id^="dropdown-"]') && !e.target.closest('[onclick*="PyxDropdown"]')) {{
                    document.querySelectorAll('[id^="dropdown-"]').forEach(el => el.classList.add('hidden'));
                }}
            }});
        </script>
        """
    
    def __str__(self):
        return self.render()


class Drawer:
    """
    Slide-out drawer/panel component.
    
    Usage:
        Drawer(
            trigger=ui.button("Open Menu"),
            content=ui.div("Drawer content here"),
            position="right",
            title="Settings"
        )
    """
    
    def __init__(
        self,
        trigger=None,
        content=None,
        position: str = "right",  # 'left', 'right', 'top', 'bottom'
        title: str = None,
        size: str = "md",  # 'sm', 'md', 'lg', 'full'
        overlay: bool = True,
        on_close: Callable = None,
        className: str = "",
        drawer_id: str = None,
    ):
        self.trigger = trigger
        self.content = content
        self.position = position
        self.title = title
        self.size = size
        self.overlay = overlay
        self.on_close = on_close
        self.className = className
        self._id = drawer_id or f"drawer-{uuid.uuid4().hex[:8]}"
        
    def render(self) -> str:
        content_html = self.content.render() if hasattr(self.content, 'render') else str(self.content) if self.content else ""
        trigger_html = ""
        if self.trigger:
            trigger_inner = self.trigger.render() if hasattr(self.trigger, 'render') else str(self.trigger)
            trigger_html = f'<div onclick="PyxDrawer.open(\'{self._id}\')">{trigger_inner}</div>'
        
        # Size classes
        sizes = {
            "sm": "max-w-sm" if self.position in ["left", "right"] else "max-h-64",
            "md": "max-w-md" if self.position in ["left", "right"] else "max-h-96",
            "lg": "max-w-lg" if self.position in ["left", "right"] else "max-h-[70vh]",
            "full": "max-w-full" if self.position in ["left", "right"] else "max-h-full",
        }
        size_class = sizes.get(self.size, sizes["md"])
        
        # Position styles
        if self.position == "right":
            panel_class = f"fixed top-0 right-0 h-full w-full {size_class} transform translate-x-full"
            animate_open = "translate-x-0"
        elif self.position == "left":
            panel_class = f"fixed top-0 left-0 h-full w-full {size_class} transform -translate-x-full"
            animate_open = "translate-x-0"
        elif self.position == "bottom":
            panel_class = f"fixed bottom-0 left-0 w-full h-full {size_class} transform translate-y-full"
            animate_open = "translate-y-0"
        else:  # top
            panel_class = f"fixed top-0 left-0 w-full h-full {size_class} transform -translate-y-full"
            animate_open = "translate-y-0"
        
        title_html = ""
        if self.title:
            title_html = f"""
                <div class="flex items-center justify-between p-4 border-b">
                    <h2 class="text-lg font-semibold">{self.title}</h2>
                    <button onclick="PyxDrawer.close('{self._id}')" class="p-1 hover:bg-gray-100 rounded">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                        </svg>
                    </button>
                </div>
            """
        
        overlay_html = ""
        if self.overlay:
            overlay_html = f'<div class="drawer-overlay fixed inset-0 bg-black/50 opacity-0 invisible transition-opacity" onclick="PyxDrawer.close(\'{self._id}\')"></div>'
        
        return f"""
        {trigger_html}
        
        <div id="{self._id}" class="drawer-container fixed inset-0 z-50 pointer-events-none {self.className}">
            {overlay_html}
            <div class="drawer-panel {panel_class} bg-white shadow-xl transition-transform duration-300 pointer-events-auto flex flex-col">
                {title_html}
                <div class="flex-1 overflow-auto p-4">
                    {content_html}
                </div>
            </div>
        </div>
        
        <script>
            window.PyxDrawer = window.PyxDrawer || {{
                open: function(id) {{
                    const container = document.getElementById(id);
                    const panel = container.querySelector('.drawer-panel');
                    const overlay = container.querySelector('.drawer-overlay');
                    
                    container.classList.add('pointer-events-auto');
                    panel.classList.remove('translate-x-full', '-translate-x-full', 'translate-y-full', '-translate-y-full');
                    if (overlay) {{
                        overlay.classList.remove('opacity-0', 'invisible');
                        overlay.classList.add('opacity-100');
                    }}
                    document.body.style.overflow = 'hidden';
                }},
                
                close: function(id) {{
                    const container = document.getElementById(id);
                    const panel = container.querySelector('.drawer-panel');
                    const overlay = container.querySelector('.drawer-overlay');
                    
                    // Determine which direction to animate
                    if (panel.classList.contains('right-0')) panel.classList.add('translate-x-full');
                    else if (panel.classList.contains('left-0') && panel.classList.contains('top-0')) panel.classList.add('-translate-x-full');
                    else if (panel.classList.contains('bottom-0')) panel.classList.add('translate-y-full');
                    else panel.classList.add('-translate-y-full');
                    
                    if (overlay) {{
                        overlay.classList.add('opacity-0');
                        setTimeout(() => overlay.classList.add('invisible'), 300);
                    }}
                    
                    setTimeout(() => {{
                        container.classList.remove('pointer-events-auto');
                        document.body.style.overflow = '';
                    }}, 300);
                }}
            }};
        </script>
        """
    
    def __str__(self):
        return self.render()


class Pagination:
    """
    Pagination component.
    
    Usage:
        Pagination(
            total=100,
            page_size=10,
            current=1,
            on_change=handle_page_change
        )
    """
    
    def __init__(
        self,
        total: int,
        page_size: int = 10,
        current: int = 1,
        on_change: Callable = None,
        show_info: bool = True,
        max_buttons: int = 5,
        className: str = "",
    ):
        self.total = total
        self.page_size = page_size
        self.current = current
        self.on_change = on_change
        self.show_info = show_info
        self.max_buttons = max_buttons
        self.className = className
        self._id = f"pagination-{uuid.uuid4().hex[:8]}"
        
    @property
    def total_pages(self):
        return max(1, (self.total + self.page_size - 1) // self.page_size)
    
    def render(self) -> str:
        total_pages = self.total_pages
        
        # Calculate visible page range
        start = max(1, self.current - self.max_buttons // 2)
        end = min(total_pages, start + self.max_buttons - 1)
        start = max(1, end - self.max_buttons + 1)
        
        # Page change handler
        change_handler = ""
        if self.on_change:
            from ..core.events import EventManager
            handler_name = EventManager.register(self.on_change)
            change_handler = f"""
                window.ws.send(JSON.stringify({{
                    type: 'event',
                    handler: '{handler_name}',
                    data: {{ page: page }}
                }}));
            """
        
        # Build page buttons
        pages_html = []
        
        # Previous button
        prev_disabled = "opacity-50 cursor-not-allowed" if self.current <= 1 else "hover:bg-gray-100"
        prev_onclick = "disabled" if self.current <= 1 else f"onclick=\"PyxPagination.goto('{self._id}', {self.current - 1})\""
        
        pages_html.append(f'''
            <button class="p-2 rounded {prev_disabled}" {prev_onclick}>
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                </svg>
            </button>
        ''')
        
        # First page
        if start > 1:
            pages_html.append(f'<button class="w-10 h-10 rounded hover:bg-gray-100" onclick="PyxPagination.goto(\'{self._id}\', 1)">1</button>')
            if start > 2:
                pages_html.append('<span class="px-2">...</span>')
        
        # Page numbers
        for page in range(start, end + 1):
            is_current = page == self.current
            btn_class = "bg-blue-600 text-white" if is_current else "hover:bg-gray-100"
            pages_html.append(f'''
                <button class="w-10 h-10 rounded {btn_class}" onclick="PyxPagination.goto('{self._id}', {page})">
                    {page}
                </button>
            ''')
        
        # Last page
        if end < total_pages:
            if end < total_pages - 1:
                pages_html.append('<span class="px-2">...</span>')
            pages_html.append(f'<button class="w-10 h-10 rounded hover:bg-gray-100" onclick="PyxPagination.goto(\'{self._id}\', {total_pages})">{total_pages}</button>')
        
        # Next button
        next_disabled = "opacity-50 cursor-not-allowed" if self.current >= total_pages else "hover:bg-gray-100"
        next_onclick = "disabled" if self.current >= total_pages else f"onclick=\"PyxPagination.goto('{self._id}', {self.current + 1})\""
        
        pages_html.append(f'''
            <button class="p-2 rounded {next_disabled}" {next_onclick}>
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
            </button>
        ''')
        
        # Info text
        info_html = ""
        if self.show_info:
            start_item = (self.current - 1) * self.page_size + 1
            end_item = min(self.current * self.page_size, self.total)
            info_html = f'<span class="text-sm text-gray-500">Showing {start_item}-{end_item} of {self.total}</span>'
        
        return f"""
        <div id="{self._id}" class="flex items-center justify-between {self.className}">
            {info_html}
            <div class="flex items-center gap-1">
                {"".join(pages_html)}
            </div>
        </div>
        
        <script>
            window.PyxPagination = window.PyxPagination || {{
                goto: function(id, page) {{
                    {change_handler}
                }}
            }};
        </script>
        """
    
    def __str__(self):
        return self.render()
