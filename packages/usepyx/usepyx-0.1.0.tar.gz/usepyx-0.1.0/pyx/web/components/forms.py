"""
PyX Form Components
Enhanced form elements and utilities.
"""
from typing import List, Dict, Any, Optional, Callable
import uuid
import json


class FormField:
    """
    Form field wrapper with label, error, and helper text.
    
    Usage:
        FormField(
            ui.input(placeholder="Enter email"),
            label="Email",
            error="Invalid email format",
            helper="We'll never share your email"
        )
    """
    
    def __init__(
        self,
        input_element,
        label: str = None,
        error: str = None,
        helper: str = None,
        required: bool = False,
        className: str = "",
    ):
        self.input_element = input_element
        self.label = label
        self.error = error
        self.helper = helper
        self.required = required
        self.className = className
        self._id = f"field-{uuid.uuid4().hex[:8]}"
    
    def render(self) -> str:
        input_html = self.input_element.render() if hasattr(self.input_element, 'render') else str(self.input_element)
        
        label_html = ""
        if self.label:
            req = '<span class="text-red-500 ml-1">*</span>' if self.required else ""
            label_html = f'<label class="block text-sm font-medium text-gray-700 mb-1">{self.label}{req}</label>'
        
        error_html = ""
        if self.error:
            error_html = f'<p class="text-sm text-red-600 mt-1">{self.error}</p>'
        
        helper_html = ""
        if self.helper and not self.error:
            helper_html = f'<p class="text-sm text-gray-500 mt-1">{self.helper}</p>'
        
        border_class = "border-red-500" if self.error else ""
        
        return f'''
        <div class="form-field {self.className}">
            {label_html}
            <div class="{border_class}">{input_html}</div>
            {error_html}
            {helper_html}
        </div>
        '''
    
    def __str__(self):
        return self.render()


class SearchInput:
    """
    Search input with autocomplete suggestions.
    
    Usage:
        SearchInput(
            placeholder="Search products...",
            suggestions=["Apple", "Banana", "Cherry"],
            on_select=handle_select
        )
    """
    
    def __init__(
        self,
        placeholder: str = "Search...",
        suggestions: List[str] = None,
        on_search: Callable = None,
        on_select: Callable = None,
        debounce: int = 300,
        className: str = "",
    ):
        self.placeholder = placeholder
        self.suggestions = suggestions or []
        self.on_search = on_search
        self.on_select = on_select
        self.debounce = debounce
        self.className = className
        self._id = f"search-{uuid.uuid4().hex[:8]}"
    
    def render(self) -> str:
        suggestions_json = json.dumps(self.suggestions)
        
        search_handler = ""
        if self.on_search:
            from ..core.events import EventManager
            handler_name = EventManager.register(self.on_search)
            search_handler = f"""
                clearTimeout(window.searchTimeout);
                window.searchTimeout = setTimeout(() => {{
                    window.ws.send(JSON.stringify({{
                        type: 'event',
                        handler: '{handler_name}',
                        data: {{ query: input.value }}
                    }}));
                }}, {self.debounce});
            """
        
        select_handler = ""
        if self.on_select:
            from ..core.events import EventManager
            handler_name = EventManager.register(self.on_select)
            select_handler = f"""
                window.ws.send(JSON.stringify({{
                    type: 'event',
                    handler: '{handler_name}',
                    data: {{ value: value }}
                }}));
            """
        
        return f'''
        <div id="{self._id}" class="relative {self.className}">
            <div class="relative">
                <i data-lucide="search" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"></i>
                <input 
                    type="text"
                    class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="{self.placeholder}"
                    oninput="PyxSearch.filter('{self._id}', this)"
                    onfocus="PyxSearch.show('{self._id}')"
                >
            </div>
            <div id="{self._id}-results" class="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto hidden z-50">
            </div>
        </div>
        
        <script>
            window.PyxSearch = window.PyxSearch || {{
                suggestions: {{}},
                
                init: function(id, items) {{
                    this.suggestions[id] = items;
                }},
                
                filter: function(id, input) {{
                    const query = input.value.toLowerCase();
                    const items = this.suggestions[id] || [];
                    const filtered = items.filter(item => item.toLowerCase().includes(query));
                    
                    const results = document.getElementById(id + '-results');
                    if (filtered.length && query) {{
                        results.innerHTML = filtered.slice(0, 10).map(item => `
                            <div class="px-4 py-2 hover:bg-gray-100 cursor-pointer" onclick="PyxSearch.select('${{id}}', '${{item}}')">
                                ${{item}}
                            </div>
                        `).join('');
                        results.classList.remove('hidden');
                    }} else {{
                        results.classList.add('hidden');
                    }}
                    
                    {search_handler}
                }},
                
                select: function(id, value) {{
                    const container = document.getElementById(id);
                    const input = container.querySelector('input');
                    input.value = value;
                    document.getElementById(id + '-results').classList.add('hidden');
                    {select_handler}
                }},
                
                show: function(id) {{
                    const input = document.querySelector(`#${{id}} input`);
                    if (input.value) this.filter(id, input);
                }},
                
                hide: function(id) {{
                    document.getElementById(id + '-results').classList.add('hidden');
                }}
            }};
            
            PyxSearch.init('{self._id}', {suggestions_json});
            
            document.addEventListener('click', (e) => {{
                if (!e.target.closest('#{self._id}')) {{
                    PyxSearch.hide('{self._id}');
                }}
            }});
        </script>
        '''
    
    def __str__(self):
        return self.render()


class Rating:
    """
    Star rating component.
    
    Usage:
        Rating(value=4, max=5, on_change=handle_rating)
        Rating(value=3.5, readonly=True)  # Half stars
    """
    
    def __init__(
        self,
        value: float = 0,
        max: int = 5,
        on_change: Callable = None,
        readonly: bool = False,
        size: str = "md",
        color: str = "yellow",
        className: str = "",
    ):
        self.value = value
        self.max = max
        self.on_change = on_change
        self.readonly = readonly
        self.size = size
        self.color = color
        self.className = className
        self._id = f"rating-{uuid.uuid4().hex[:8]}"
    
    def render(self) -> str:
        sizes = {"sm": "w-4 h-4", "md": "w-6 h-6", "lg": "w-8 h-8"}
        size_class = sizes.get(self.size, sizes["md"])
        
        stars_html = []
        for i in range(1, self.max + 1):
            filled = i <= self.value
            half = not filled and i - 0.5 <= self.value
            
            if filled:
                fill = f"fill-{self.color}-400 text-{self.color}-400"
            elif half:
                fill = f"fill-{self.color}-400/50 text-{self.color}-400"
            else:
                fill = "fill-gray-200 text-gray-300"
            
            cursor = "cursor-pointer hover:scale-110" if not self.readonly else ""
            onclick = f"onclick=\"PyxRating.set('{self._id}', {i})\"" if not self.readonly else ""
            
            stars_html.append(f'''
                <svg class="{size_class} {fill} {cursor} transition-transform" {onclick} viewBox="0 0 24 24">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
            ''')
        
        change_handler = ""
        if self.on_change:
            from ..core.events import EventManager
            handler_name = EventManager.register(self.on_change)
            change_handler = f'''
                window.ws.send(JSON.stringify({{
                    type: 'event',
                    handler: '{handler_name}',
                    data: {{ value: value }}
                }}));
            '''
        
        return f'''
        <div id="{self._id}" class="flex items-center gap-1 {self.className}" data-value="{self.value}">
            {"".join(stars_html)}
        </div>
        
        <script>
            window.PyxRating = window.PyxRating || {{
                set: function(id, value) {{
                    const container = document.getElementById(id);
                    container.dataset.value = value;
                    // Re-render stars
                    const stars = container.querySelectorAll('svg');
                    stars.forEach((star, i) => {{
                        const filled = (i + 1) <= value;
                        star.classList.toggle('fill-yellow-400', filled);
                        star.classList.toggle('text-yellow-400', filled);
                        star.classList.toggle('fill-gray-200', !filled);
                        star.classList.toggle('text-gray-300', !filled);
                    }});
                    {change_handler}
                }}
            }};
        </script>
        '''
    
    def __str__(self):
        return self.render()


class CopyButton:
    """
    Copy to clipboard button.
    
    Usage:
        CopyButton(text="secret-api-key-123")
        CopyButton(text=code_content, label="Copy Code")
    """
    
    def __init__(
        self,
        text: str,
        label: str = "Copy",
        copied_label: str = "Copied!",
        variant: str = "default",  # 'default', 'icon'
        className: str = "",
    ):
        self.text = text
        self.label = label
        self.copied_label = copied_label
        self.variant = variant
        self.className = className
        self._id = f"copy-{uuid.uuid4().hex[:8]}"
    
    def render(self) -> str:
        text_escaped = self.text.replace("'", "\\'").replace("\n", "\\n")
        
        if self.variant == "icon":
            return f'''
            <button id="{self._id}" class="p-2 hover:bg-gray-100 rounded transition-colors {self.className}"
                    onclick="PyxCopy.copy('{self._id}', '{text_escaped}')">
                <svg class="copy-icon w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                </svg>
                <svg class="check-icon w-4 h-4 hidden text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
            </button>
            '''
        
        return f'''
        <button id="{self._id}" class="px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 rounded transition-colors {self.className}"
                onclick="PyxCopy.copy('{self._id}', '{text_escaped}')">
            <span class="label">{self.label}</span>
            <span class="copied hidden text-green-600">{self.copied_label}</span>
        </button>
        
        <script>
            window.PyxCopy = window.PyxCopy || {{
                copy: async function(id, text) {{
                    await navigator.clipboard.writeText(text);
                    const btn = document.getElementById(id);
                    
                    // Toggle visible elements
                    const label = btn.querySelector('.label, .copy-icon');
                    const copied = btn.querySelector('.copied, .check-icon');
                    
                    if (label) label.classList.add('hidden');
                    if (copied) copied.classList.remove('hidden');
                    
                    setTimeout(() => {{
                        if (label) label.classList.remove('hidden');
                        if (copied) copied.classList.add('hidden');
                    }}, 2000);
                }}
            }};
        </script>
        '''
    
    def __str__(self):
        return self.render()


class Toggle:
    """
    Toggle/Switch component.
    
    Usage:
        Toggle(value=True, on_change=handle_toggle)
        Toggle(label="Enable notifications")
    """
    
    def __init__(
        self,
        value: bool = False,
        label: str = None,
        on_change: Callable = None,
        disabled: bool = False,
        size: str = "md",
        className: str = "",
    ):
        self.value = value
        self.label = label
        self.on_change = on_change
        self.disabled = disabled
        self.size = size
        self.className = className
        self._id = f"toggle-{uuid.uuid4().hex[:8]}"
    
    def render(self) -> str:
        sizes = {
            "sm": {"track": "w-8 h-4", "thumb": "w-3 h-3", "translate": "translate-x-4"},
            "md": {"track": "w-11 h-6", "thumb": "w-5 h-5", "translate": "translate-x-5"},
            "lg": {"track": "w-14 h-7", "thumb": "w-6 h-6", "translate": "translate-x-7"},
        }
        s = sizes.get(self.size, sizes["md"])
        
        checked = "checked" if self.value else ""
        disabled_class = "opacity-50 cursor-not-allowed" if self.disabled else "cursor-pointer"
        
        change_handler = ""
        if self.on_change:
            from ..core.events import EventManager
            handler_name = EventManager.register(self.on_change)
            change_handler = f'''
                window.ws.send(JSON.stringify({{
                    type: 'event',
                    handler: '{handler_name}',
                    data: {{ checked: this.checked }}
                }}));
            '''
        
        label_html = f'<span class="ml-3 text-sm text-gray-700">{self.label}</span>' if self.label else ""
        
        return f'''
        <label class="inline-flex items-center {disabled_class} {self.className}">
            <input type="checkbox" id="{self._id}" class="sr-only peer" {checked} {"disabled" if self.disabled else ""}
                   onchange="{change_handler}">
            <div class="{s['track']} bg-gray-200 rounded-full peer peer-checked:bg-blue-600 transition-colors relative">
                <div class="{s['thumb']} bg-white rounded-full shadow absolute top-0.5 left-0.5 peer-checked:{s['translate']} transition-transform"></div>
            </div>
            {label_html}
        </label>
        '''
    
    def __str__(self):
        return self.render()


class Table:
    """
    Simple table component (lighter than DataGrid).
    
    Usage:
        Table(
            headers=["Name", "Email", "Role"],
            rows=[
                ["John", "john@mail.com", "Admin"],
                ["Jane", "jane@mail.com", "User"],
            ]
        )
    """
    
    def __init__(
        self,
        headers: List[str],
        rows: List[List[Any]],
        striped: bool = True,
        hoverable: bool = True,
        bordered: bool = False,
        compact: bool = False,
        className: str = "",
    ):
        self.headers = headers
        self.rows = rows
        self.striped = striped
        self.hoverable = hoverable
        self.bordered = bordered
        self.compact = compact
        self.className = className
    
    def render(self) -> str:
        padding = "px-3 py-2" if self.compact else "px-6 py-4"
        border = "border" if self.bordered else ""
        
        # Headers
        headers_html = "".join([f'<th class="{padding} text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{h}</th>' for h in self.headers])
        
        # Rows
        rows_html = []
        for i, row in enumerate(self.rows):
            stripe = "bg-gray-50" if self.striped and i % 2 == 1 else "bg-white"
            hover = "hover:bg-gray-100" if self.hoverable else ""
            
            cells = "".join([f'<td class="{padding} text-sm text-gray-900">{c}</td>' for c in row])
            rows_html.append(f'<tr class="{stripe} {hover}">{cells}</tr>')
        
        return f'''
        <div class="overflow-x-auto {self.className}">
            <table class="min-w-full divide-y divide-gray-200 {border}">
                <thead class="bg-gray-50">
                    <tr>{headers_html}</tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                    {"".join(rows_html)}
                </tbody>
            </table>
        </div>
        '''
    
    def __str__(self):
        return self.render()
