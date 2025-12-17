"""
PyX Developer Tools
Tools for development experience.
"""
from typing import List, Dict, Any, Optional
import uuid


# Lucide Icons - Common categories (subset for search)
LUCIDE_ICONS = {
    # Navigation
    "navigation": [
        "arrow-up", "arrow-down", "arrow-left", "arrow-right",
        "chevron-up", "chevron-down", "chevron-left", "chevron-right",
        "home", "menu", "x", "more-horizontal", "more-vertical",
        "external-link", "link", "corner-up-left", "corner-up-right",
    ],
    # Actions
    "actions": [
        "plus", "minus", "check", "x", "edit", "trash", "trash-2",
        "copy", "clipboard", "download", "upload", "share", "share-2",
        "save", "refresh-cw", "rotate-cw", "rotate-ccw", "undo", "redo",
        "search", "zoom-in", "zoom-out", "filter", "settings", "sliders",
    ],
    # Media
    "media": [
        "image", "video", "camera", "mic", "volume", "volume-2",
        "play", "pause", "stop", "skip-forward", "skip-back",
        "maximize", "minimize", "fullscreen", "picture-in-picture",
    ],
    # Communication
    "communication": [
        "mail", "inbox", "send", "message-circle", "message-square",
        "phone", "phone-call", "video", "at-sign", "bell", "bell-off",
    ],
    # User
    "user": [
        "user", "users", "user-plus", "user-minus", "user-check",
        "user-x", "log-in", "log-out", "key", "lock", "unlock",
    ],
    # Commerce
    "commerce": [
        "shopping-cart", "shopping-bag", "credit-card", "dollar-sign",
        "percent", "tag", "tags", "receipt", "wallet", "gift",
    ],
    # Data
    "data": [
        "database", "server", "hard-drive", "cloud", "cloud-upload",
        "cloud-download", "folder", "file", "file-text", "files",
    ],
    # Charts
    "charts": [
        "bar-chart", "bar-chart-2", "line-chart", "pie-chart",
        "trending-up", "trending-down", "activity", "signal",
    ],
    # Status
    "status": [
        "check-circle", "x-circle", "alert-circle", "alert-triangle",
        "info", "help-circle", "loader", "hourglass", "clock",
    ],
    # Layout
    "layout": [
        "layout", "grid", "list", "columns", "rows", "sidebar",
        "panel-left", "panel-right", "maximize-2", "minimize-2",
    ],
    # Social
    "social": [
        "github", "twitter", "facebook", "instagram", "linkedin",
        "youtube", "twitch", "discord", "slack", "dribbble",
    ],
    # Weather
    "weather": [
        "sun", "moon", "cloud", "cloud-rain", "cloud-snow",
        "wind", "thermometer", "droplet", "umbrella",
    ],
    # Objects
    "objects": [
        "calendar", "bookmark", "flag", "globe", "map", "map-pin",
        "compass", "navigation", "anchor", "target", "crosshair",
        "heart", "star", "zap", "flame", "coffee", "gift",
    ],
}


class IconBrowser:
    """
    Lucide Icon Browser/Search component.
    
    Usage:
        IconBrowser()  # Full browser modal
    """
    
    def __init__(self, on_select=None, className: str = ""):
        self.on_select = on_select
        self.className = className
        self._id = f"icon-browser-{uuid.uuid4().hex[:8]}"
    
    @staticmethod
    def search(query: str) -> List[str]:
        """Search icons by name"""
        query = query.lower()
        results = []
        for category, icons in LUCIDE_ICONS.items():
            for icon in icons:
                if query in icon:
                    results.append(icon)
        return results
    
    @staticmethod
    def all() -> Dict[str, List[str]]:
        """Get all icons by category"""
        return LUCIDE_ICONS
    
    @staticmethod
    def category(name: str) -> List[str]:
        """Get icons in a category"""
        return LUCIDE_ICONS.get(name, [])
    
    def render(self) -> str:
        # Build icon grid
        all_icons = []
        for category, icons in LUCIDE_ICONS.items():
            all_icons.extend(icons)
        
        # Remove duplicates
        all_icons = list(set(all_icons))
        all_icons.sort()
        
        icons_html = ""
        for icon in all_icons:
            icons_html += f'''
                <div class="icon-item p-3 rounded-lg hover:bg-gray-100 cursor-pointer flex flex-col items-center gap-1 text-center"
                     data-icon="{icon}" onclick="PyxIconBrowser.select('{self._id}', '{icon}')">
                    <i data-lucide="{icon}" class="w-6 h-6"></i>
                    <span class="text-xs text-gray-500 truncate w-full">{icon}</span>
                </div>
            '''
        
        return f'''
        <div id="{self._id}" class="icon-browser {self.className}">
            <!-- Trigger Button -->
            <button onclick="PyxIconBrowser.open('{self._id}')" 
                    class="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm flex items-center gap-2">
                <i data-lucide="search" class="w-4 h-4"></i>
                Browse Icons
            </button>
            
            <!-- Modal -->
            <div class="icon-modal hidden fixed inset-0 z-50 bg-black/50 flex items-center justify-center">
                <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col">
                    <!-- Header -->
                    <div class="flex items-center gap-3 p-4 border-b">
                        <i data-lucide="search" class="w-5 h-5 text-gray-400"></i>
                        <input type="text" 
                               placeholder="Search 200+ icons..."
                               class="flex-1 outline-none text-lg"
                               oninput="PyxIconBrowser.filter('{self._id}', this.value)">
                        <button onclick="PyxIconBrowser.close('{self._id}')" class="p-1 hover:bg-gray-100 rounded">
                            <i data-lucide="x" class="w-5 h-5"></i>
                        </button>
                    </div>
                    
                    <!-- Icon Grid -->
                    <div class="flex-1 overflow-y-auto p-4">
                        <div class="icon-grid grid grid-cols-6 gap-2">
                            {icons_html}
                        </div>
                    </div>
                    
                    <!-- Footer -->
                    <div class="p-3 border-t bg-gray-50 text-center text-sm text-gray-500">
                        <span class="selected-icon">Click an icon to copy</span>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            window.PyxIconBrowser = window.PyxIconBrowser || {{
                open: function(id) {{
                    const container = document.getElementById(id);
                    container.querySelector('.icon-modal').classList.remove('hidden');
                    container.querySelector('input').focus();
                    lucide.createIcons();
                }},
                
                close: function(id) {{
                    const container = document.getElementById(id);
                    container.querySelector('.icon-modal').classList.add('hidden');
                }},
                
                filter: function(id, query) {{
                    const container = document.getElementById(id);
                    const items = container.querySelectorAll('.icon-item');
                    query = query.toLowerCase();
                    
                    items.forEach(item => {{
                        const name = item.dataset.icon;
                        item.style.display = name.includes(query) ? '' : 'none';
                    }});
                }},
                
                select: function(id, iconName) {{
                    // Copy to clipboard
                    navigator.clipboard.writeText(iconName);
                    
                    // Show feedback
                    const container = document.getElementById(id);
                    const footer = container.querySelector('.selected-icon');
                    footer.innerHTML = `<span class="text-green-600">Copied: <code class="bg-gray-200 px-1 rounded">${{iconName}}</code></span>`;
                    
                    setTimeout(() => {{
                        footer.textContent = 'Click an icon to copy';
                    }}, 2000);
                }}
            }};
        </script>
        '''
    
    def __str__(self):
        return self.render()


class ResponsivePreview:
    """
    Responsive preview wrapper for development.
    
    Usage:
        ResponsivePreview(content, device="iphone-14")
    """
    
    DEVICES = {
        "iphone-se": {"width": 375, "height": 667, "name": "iPhone SE"},
        "iphone-14": {"width": 390, "height": 844, "name": "iPhone 14"},
        "iphone-14-pro-max": {"width": 430, "height": 932, "name": "iPhone 14 Pro Max"},
        "ipad": {"width": 768, "height": 1024, "name": "iPad"},
        "ipad-pro": {"width": 1024, "height": 1366, "name": "iPad Pro"},
        "pixel-7": {"width": 412, "height": 915, "name": "Pixel 7"},
        "galaxy-s23": {"width": 360, "height": 780, "name": "Galaxy S23"},
        "desktop-sm": {"width": 1280, "height": 800, "name": "Desktop SM"},
        "desktop-lg": {"width": 1920, "height": 1080, "name": "Desktop LG"},
    }
    
    def __init__(self, content=None, device: str = "iphone-14", className: str = ""):
        self.content = content
        self.device = device
        self.className = className
        self._id = f"preview-{uuid.uuid4().hex[:8]}"
    
    def render(self) -> str:
        device_info = self.DEVICES.get(self.device, self.DEVICES["iphone-14"])
        content_html = self.content.render() if hasattr(self.content, 'render') else str(self.content) if self.content else ""
        
        # Device options
        options_html = ""
        for key, info in self.DEVICES.items():
            selected = "selected" if key == self.device else ""
            options_html += f'<option value="{key}" {selected}>{info["name"]} ({info["width"]}x{info["height"]})</option>'
        
        return f'''
        <div id="{self._id}" class="responsive-preview {self.className}">
            <!-- Toolbar -->
            <div class="flex items-center gap-4 p-4 bg-gray-100 rounded-t-xl border border-b-0">
                <select onchange="PyxPreview.setDevice('{self._id}', this.value)"
                        class="px-3 py-1.5 bg-white border rounded-lg text-sm">
                    {options_html}
                </select>
                
                <div class="flex items-center gap-2">
                    <button onclick="PyxPreview.rotate('{self._id}')" 
                            class="p-2 hover:bg-gray-200 rounded-lg" title="Rotate">
                        <i data-lucide="rotate-cw" class="w-4 h-4"></i>
                    </button>
                    <button onclick="PyxPreview.zoomIn('{self._id}')" 
                            class="p-2 hover:bg-gray-200 rounded-lg" title="Zoom In">
                        <i data-lucide="zoom-in" class="w-4 h-4"></i>
                    </button>
                    <button onclick="PyxPreview.zoomOut('{self._id}')" 
                            class="p-2 hover:bg-gray-200 rounded-lg" title="Zoom Out">
                        <i data-lucide="zoom-out" class="w-4 h-4"></i>
                    </button>
                </div>
                
                <span class="text-sm text-gray-500 ml-auto device-info">
                    {device_info["name"]} • {device_info["width"]}×{device_info["height"]}
                </span>
            </div>
            
            <!-- Preview Container -->
            <div class="preview-container bg-gray-200 p-8 flex items-center justify-center overflow-auto rounded-b-xl border"
                 style="min-height: 600px;">
                <div class="preview-frame bg-black rounded-[2rem] p-2 shadow-2xl transition-all">
                    <div class="preview-screen bg-white overflow-auto rounded-[1.5rem]"
                         style="width: {device_info["width"]}px; height: {device_info["height"]}px;">
                        <iframe class="w-full h-full border-0" srcdoc='{content_html.replace("'", "&#39;")}'></iframe>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            window.PyxPreview = window.PyxPreview || {{
                devices: {str(self.DEVICES).replace("'", '"')},
                zoom: 1,
                rotated: false,
                
                setDevice: function(id, device) {{
                    const container = document.getElementById(id);
                    const screen = container.querySelector('.preview-screen');
                    const info = container.querySelector('.device-info');
                    const d = this.devices[device];
                    
                    screen.style.width = (this.rotated ? d.height : d.width) + 'px';
                    screen.style.height = (this.rotated ? d.width : d.height) + 'px';
                    info.textContent = d.name + ' • ' + d.width + '×' + d.height;
                }},
                
                rotate: function(id) {{
                    const container = document.getElementById(id);
                    const screen = container.querySelector('.preview-screen');
                    const w = screen.style.width;
                    screen.style.width = screen.style.height;
                    screen.style.height = w;
                    this.rotated = !this.rotated;
                }},
                
                zoomIn: function(id) {{
                    this.zoom = Math.min(2, this.zoom + 0.1);
                    this.applyZoom(id);
                }},
                
                zoomOut: function(id) {{
                    this.zoom = Math.max(0.3, this.zoom - 0.1);
                    this.applyZoom(id);
                }},
                
                applyZoom: function(id) {{
                    const container = document.getElementById(id);
                    const frame = container.querySelector('.preview-frame');
                    frame.style.transform = `scale(${{this.zoom}})`;
                }}
            }};
        </script>
        '''
    
    def __str__(self):
        return self.render()


class DevToolbar:
    """
    Floating development toolbar.
    
    Usage:
        DevToolbar()  # Include in dev mode
    """
    
    def __init__(self, show_grid: bool = False, show_breakpoints: bool = True):
        self.show_grid = show_grid
        self.show_breakpoints = show_breakpoints
        self._id = "pyx-dev-toolbar"
    
    def render(self) -> str:
        return f'''
        <div id="{self._id}" class="fixed bottom-4 left-1/2 -translate-x-1/2 z-[9999] bg-gray-900 text-white rounded-full shadow-2xl px-4 py-2 flex items-center gap-4 text-sm">
            <!-- Viewport Info -->
            <span class="viewport-info font-mono">--</span>
            
            <!-- Breakpoint Indicator -->
            <div class="breakpoint-indicator flex items-center gap-1">
                <span class="hidden sm:inline text-green-400">sm</span>
                <span class="hidden md:inline text-blue-400">md</span>
                <span class="hidden lg:inline text-purple-400">lg</span>
                <span class="hidden xl:inline text-pink-400">xl</span>
                <span class="hidden 2xl:inline text-orange-400">2xl</span>
            </div>
            
            <!-- Actions -->
            <div class="flex items-center gap-2 border-l border-gray-700 pl-4">
                <button onclick="PyxDevTools.toggleGrid()" class="p-1 hover:bg-gray-700 rounded" title="Toggle Grid">
                    <i data-lucide="grid" class="w-4 h-4"></i>
                </button>
                <button onclick="PyxDevTools.toggleOutlines()" class="p-1 hover:bg-gray-700 rounded" title="Toggle Outlines">
                    <i data-lucide="square" class="w-4 h-4"></i>
                </button>
                <button onclick="PyxDevTools.openIcons()" class="p-1 hover:bg-gray-700 rounded" title="Icon Browser">
                    <i data-lucide="smile" class="w-4 h-4"></i>
                </button>
            </div>
        </div>
        
        <!-- Grid Overlay -->
        <div id="pyx-grid-overlay" class="fixed inset-0 pointer-events-none z-[9998] hidden">
            <div class="container mx-auto h-full">
                <div class="grid grid-cols-12 gap-4 h-full">
                    {''.join(['<div class="bg-blue-500/10 border-x border-blue-500/20"></div>' for _ in range(12)])}
                </div>
            </div>
        </div>
        
        <style>
            .pyx-outline-mode * {{
                outline: 1px solid rgba(59, 130, 246, 0.3) !important;
            }}
        </style>
        
        <script>
            window.PyxDevTools = window.PyxDevTools || {{
                gridVisible: false,
                outlinesVisible: false,
                
                init: function() {{
                    this.updateViewport();
                    window.addEventListener('resize', () => this.updateViewport());
                    lucide.createIcons();
                }},
                
                updateViewport: function() {{
                    const info = document.querySelector('.viewport-info');
                    if (info) {{
                        info.textContent = window.innerWidth + '×' + window.innerHeight;
                    }}
                }},
                
                toggleGrid: function() {{
                    this.gridVisible = !this.gridVisible;
                    document.getElementById('pyx-grid-overlay').classList.toggle('hidden', !this.gridVisible);
                }},
                
                toggleOutlines: function() {{
                    this.outlinesVisible = !this.outlinesVisible;
                    document.body.classList.toggle('pyx-outline-mode', this.outlinesVisible);
                }},
                
                openIcons: function() {{
                    // Trigger icon browser if exists
                    const browser = document.querySelector('[id^="icon-browser-"]');
                    if (browser) {{
                        PyxIconBrowser.open(browser.id);
                    }}
                }}
            }};
            
            PyxDevTools.init();
        </script>
        '''
    
    def __str__(self):
        return self.render()
