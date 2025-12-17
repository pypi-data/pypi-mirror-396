"""
PyX Toast/Notification System
Beautiful toast notifications.
"""
from typing import Optional, Callable
import uuid


class Toast:
    """
    Toast notification system.
    
    Usage (in Python handler):
        return Toast.success("Item saved!")
        return Toast.error("Something went wrong", duration=5000)
        return Toast.info("Did you know?", action="Learn More")
    
    Usage (in View - container):
        ToastContainer(position="top-right")
    """
    
    @staticmethod
    def success(message: str, title: str = None, duration: int = 3000, action: str = None) -> dict:
        return {"type": "toast", "variant": "success", "message": message, "title": title, "duration": duration, "action": action}
    
    @staticmethod
    def error(message: str, title: str = None, duration: int = 5000, action: str = None) -> dict:
        return {"type": "toast", "variant": "error", "message": message, "title": title, "duration": duration, "action": action}
    
    @staticmethod
    def warning(message: str, title: str = None, duration: int = 4000, action: str = None) -> dict:
        return {"type": "toast", "variant": "warning", "message": message, "title": title, "duration": duration, "action": action}
    
    @staticmethod
    def info(message: str, title: str = None, duration: int = 3000, action: str = None) -> dict:
        return {"type": "toast", "variant": "info", "message": message, "title": title, "duration": duration, "action": action}
    
    @staticmethod
    def custom(message: str, icon: str = None, color: str = "blue", duration: int = 3000) -> dict:
        return {"type": "toast", "variant": "custom", "message": message, "icon": icon, "color": color, "duration": duration}


class ToastContainer:
    """
    Container for toast notifications.
    Include once in your layout.
    
    Usage:
        ToastContainer(position="top-right")
    """
    
    POSITIONS = {
        "top-right": "top-4 right-4",
        "top-left": "top-4 left-4",
        "top-center": "top-4 left-1/2 -translate-x-1/2",
        "bottom-right": "bottom-4 right-4",
        "bottom-left": "bottom-4 left-4",
        "bottom-center": "bottom-4 left-1/2 -translate-x-1/2",
    }
    
    def __init__(self, position: str = "top-right", max_toasts: int = 5):
        self.position = position
        self.max_toasts = max_toasts
        self._id = "pyx-toast-container"
    
    def render(self) -> str:
        pos_class = self.POSITIONS.get(self.position, self.POSITIONS["top-right"])
        
        return f'''
        <div id="{self._id}" class="fixed {pos_class} z-[100] flex flex-col gap-2 pointer-events-none">
        </div>
        
        <script>
            window.PyxToast = window.PyxToast || {{
                container: null,
                maxToasts: {self.max_toasts},
                
                init: function() {{
                    this.container = document.getElementById('{self._id}');
                }},
                
                show: function(options) {{
                    if (!this.container) this.init();
                    
                    const id = 'toast-' + Date.now();
                    const toast = document.createElement('div');
                    toast.id = id;
                    toast.className = this.getClasses(options.variant);
                    toast.innerHTML = this.getContent(options);
                    
                    // Add to container
                    this.container.appendChild(toast);
                    
                    // Animate in
                    requestAnimationFrame(() => {{
                        toast.classList.remove('translate-x-full', 'opacity-0');
                    }});
                    
                    // Auto dismiss
                    if (options.duration > 0) {{
                        setTimeout(() => this.dismiss(id), options.duration);
                    }}
                    
                    // Limit toasts
                    const toasts = this.container.children;
                    while (toasts.length > this.maxToasts) {{
                        toasts[0].remove();
                    }}
                    
                    return id;
                }},
                
                dismiss: function(id) {{
                    const toast = document.getElementById(id);
                    if (toast) {{
                        toast.classList.add('translate-x-full', 'opacity-0');
                        setTimeout(() => toast.remove(), 300);
                    }}
                }},
                
                getClasses: function(variant) {{
                    const base = 'pointer-events-auto flex items-start gap-3 p-4 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full opacity-0 min-w-[300px] max-w-md';
                    const variants = {{
                        success: 'bg-green-50 border border-green-200 text-green-800',
                        error: 'bg-red-50 border border-red-200 text-red-800',
                        warning: 'bg-yellow-50 border border-yellow-200 text-yellow-800',
                        info: 'bg-blue-50 border border-blue-200 text-blue-800',
                        custom: 'bg-white border border-gray-200 text-gray-800',
                    }};
                    return base + ' ' + (variants[variant] || variants.info);
                }},
                
                getContent: function(options) {{
                    const icons = {{
                        success: '<svg class="w-5 h-5 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
                        error: '<svg class="w-5 h-5 text-red-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
                        warning: '<svg class="w-5 h-5 text-yellow-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>',
                        info: '<svg class="w-5 h-5 text-blue-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
                    }};
                    
                    const icon = options.icon ? `<i data-lucide="${{options.icon}}" class="w-5 h-5 flex-shrink-0"></i>` : (icons[options.variant] || icons.info);
                    const title = options.title ? `<p class="font-semibold">${{options.title}}</p>` : '';
                    const action = options.action ? `<button class="text-sm font-medium underline mt-1">${{options.action}}</button>` : '';
                    
                    return `
                        ${{icon}}
                        <div class="flex-1">
                            ${{title}}
                            <p class="text-sm">${{options.message}}</p>
                            ${{action}}
                        </div>
                        <button onclick="PyxToast.dismiss(this.parentElement.id)" class="flex-shrink-0 hover:opacity-70">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                            </svg>
                        </button>
                    `;
                }},
                
                success: function(message, options = {{}}) {{
                    return this.show({{ ...options, variant: 'success', message }});
                }},
                
                error: function(message, options = {{}}) {{
                    return this.show({{ ...options, variant: 'error', message, duration: options.duration || 5000 }});
                }},
                
                warning: function(message, options = {{}}) {{
                    return this.show({{ ...options, variant: 'warning', message }});
                }},
                
                info: function(message, options = {{}}) {{
                    return this.show({{ ...options, variant: 'info', message }});
                }}
            }};
            
            PyxToast.init();
        </script>
        '''
    
    def __str__(self):
        return self.render()


class Notification:
    """
    Inline notification banner.
    
    Usage:
        Notification(
            message="Your trial expires in 3 days",
            variant="warning",
            action="Upgrade Now",
            on_action=handle_upgrade
        )
    """
    
    def __init__(
        self,
        message: str,
        title: str = None,
        variant: str = "info",  # 'info', 'success', 'warning', 'error'
        icon: str = None,
        action: str = None,
        on_action: Callable = None,
        dismissible: bool = True,
        className: str = "",
    ):
        self.message = message
        self.title = title
        self.variant = variant
        self.icon = icon
        self.action = action
        self.on_action = on_action
        self.dismissible = dismissible
        self.className = className
        self._id = f"notification-{uuid.uuid4().hex[:8]}"
    
    def render(self) -> str:
        colors = {
            "info": {"bg": "bg-blue-50", "border": "border-blue-200", "text": "text-blue-800", "icon": "text-blue-600"},
            "success": {"bg": "bg-green-50", "border": "border-green-200", "text": "text-green-800", "icon": "text-green-600"},
            "warning": {"bg": "bg-yellow-50", "border": "border-yellow-200", "text": "text-yellow-800", "icon": "text-yellow-600"},
            "error": {"bg": "bg-red-50", "border": "border-red-200", "text": "text-red-800", "icon": "text-red-600"},
        }
        c = colors.get(self.variant, colors["info"])
        
        icons = {
            "info": "info",
            "success": "check-circle",
            "warning": "alert-triangle",
            "error": "x-circle",
        }
        icon_name = self.icon or icons.get(self.variant, "info")
        
        title_html = f'<p class="font-semibold">{self.title}</p>' if self.title else ""
        
        action_html = ""
        if self.action:
            action_html = f'<button class="font-medium underline hover:no-underline">{self.action}</button>'
        
        dismiss_html = ""
        if self.dismissible:
            dismiss_html = f'''
                <button onclick="document.getElementById('{self._id}').remove()" class="flex-shrink-0 hover:opacity-70">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                </button>
            '''
        
        return f'''
        <div id="{self._id}" class="flex items-start gap-3 p-4 rounded-lg border {c['bg']} {c['border']} {c['text']} {self.className}">
            <i data-lucide="{icon_name}" class="w-5 h-5 {c['icon']} flex-shrink-0 mt-0.5"></i>
            <div class="flex-1">
                {title_html}
                <p class="text-sm">{self.message}</p>
                {action_html}
            </div>
            {dismiss_html}
        </div>
        '''
    
    def __str__(self):
        return self.render()
