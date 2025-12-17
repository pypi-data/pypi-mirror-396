"""
PyX Accessibility (A11y) Utilities
Tools for building accessible applications.
"""
from typing import Optional, Dict, Any, List
import uuid


class A11y:
    """
    Accessibility attribute helpers.
    
    Usage:
        # In element chain
        ui.button("Menu").a11y(label="Open navigation menu", expanded=False)
        
        # Standalone
        attrs = A11y.button_attrs("Open menu", expanded=True)
    """
    
    @staticmethod
    def label(text: str) -> Dict[str, str]:
        """aria-label for screen readers"""
        return {"aria-label": text}
    
    @staticmethod
    def described_by(id: str) -> Dict[str, str]:
        """Link to description element"""
        return {"aria-describedby": id}
    
    @staticmethod
    def hidden(hidden: bool = True) -> Dict[str, str]:
        """Hide from screen readers"""
        return {"aria-hidden": "true" if hidden else "false"}
    
    @staticmethod
    def live(mode: str = "polite") -> Dict[str, str]:
        """Live region for dynamic updates (polite, assertive, off)"""
        return {"aria-live": mode}
    
    @staticmethod
    def role(role: str) -> Dict[str, str]:
        """Set ARIA role"""
        return {"role": role}
    
    @staticmethod
    def expanded(is_expanded: bool) -> Dict[str, str]:
        """For collapsible elements"""
        return {"aria-expanded": "true" if is_expanded else "false"}
    
    @staticmethod
    def pressed(is_pressed: bool) -> Dict[str, str]:
        """For toggle buttons"""
        return {"aria-pressed": "true" if is_pressed else "false"}
    
    @staticmethod
    def selected(is_selected: bool) -> Dict[str, str]:
        """For selectable items"""
        return {"aria-selected": "true" if is_selected else "false"}
    
    @staticmethod
    def disabled(is_disabled: bool) -> Dict[str, str]:
        """For disabled elements"""
        return {"aria-disabled": "true" if is_disabled else "false"}
    
    @staticmethod
    def current(value: str = "page") -> Dict[str, str]:
        """For current item in navigation (page, step, location, date, time, true)"""
        return {"aria-current": value}
    
    @staticmethod
    def controls(id: str) -> Dict[str, str]:
        """Element controls another element"""
        return {"aria-controls": id}
    
    @staticmethod
    def owns(id: str) -> Dict[str, str]:
        """Element owns another element"""
        return {"aria-owns": id}
    
    @staticmethod
    def haspopup(popup_type: str = "menu") -> Dict[str, str]:
        """Has popup (menu, dialog, listbox, tree, grid)"""
        return {"aria-haspopup": popup_type}
    
    # Component-specific helpers
    
    @staticmethod
    def button_attrs(label: str, expanded: bool = None, controls: str = None) -> Dict[str, str]:
        """Complete attrs for accessible button"""
        attrs = {"aria-label": label, "role": "button"}
        if expanded is not None:
            attrs["aria-expanded"] = "true" if expanded else "false"
        if controls:
            attrs["aria-controls"] = controls
        return attrs
    
    @staticmethod
    def tab_attrs(selected: bool, controls: str) -> Dict[str, str]:
        """Complete attrs for tab"""
        return {
            "role": "tab",
            "aria-selected": "true" if selected else "false",
            "aria-controls": controls,
            "tabindex": "0" if selected else "-1"
        }
    
    @staticmethod
    def tabpanel_attrs(id: str, labelledby: str) -> Dict[str, str]:
        """Complete attrs for tab panel"""
        return {
            "id": id,
            "role": "tabpanel",
            "aria-labelledby": labelledby
        }
    
    @staticmethod
    def modal_attrs(label: str) -> Dict[str, str]:
        """Complete attrs for modal dialog"""
        return {
            "role": "dialog",
            "aria-modal": "true",
            "aria-label": label
        }
    
    @staticmethod
    def alert_attrs(assertive: bool = False) -> Dict[str, str]:
        """Complete attrs for alert"""
        return {
            "role": "alert",
            "aria-live": "assertive" if assertive else "polite"
        }


class FocusTrap:
    """
    Focus trap for modals and dialogs.
    
    Usage:
        FocusTrap(ui.div(...))  # Traps focus inside the element
    """
    
    def __init__(self, content, initially_focused: str = None, className: str = ""):
        self.content = content
        self.initially_focused = initially_focused
        self.className = className
        self._id = f"focus-trap-{uuid.uuid4().hex[:8]}"
    
    def render(self) -> str:
        content_html = self.content.render() if hasattr(self.content, 'render') else str(self.content)
        
        initial_focus = f"container.querySelector('{self.initially_focused}')" if self.initially_focused else "focusable[0]"
        
        return f'''
        <div id="{self._id}" class="focus-trap {self.className}" data-focus-trap="true">
            {content_html}
        </div>
        
        <script>
            (function() {{
                const container = document.getElementById('{self._id}');
                const focusableSelectors = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
                const focusable = container.querySelectorAll(focusableSelectors);
                
                if (focusable.length === 0) return;
                
                const firstFocusable = focusable[0];
                const lastFocusable = focusable[focusable.length - 1];
                
                // Initial focus
                const initialEl = {initial_focus};
                if (initialEl) initialEl.focus();
                
                // Trap focus
                container.addEventListener('keydown', function(e) {{
                    if (e.key !== 'Tab') return;
                    
                    if (e.shiftKey) {{
                        if (document.activeElement === firstFocusable) {{
                            e.preventDefault();
                            lastFocusable.focus();
                        }}
                    }} else {{
                        if (document.activeElement === lastFocusable) {{
                            e.preventDefault();
                            firstFocusable.focus();
                        }}
                    }}
                }});
            }})();
        </script>
        '''
    
    def __str__(self):
        return self.render()


class SkipLink:
    """
    Skip to main content link for keyboard users.
    
    Usage:
        SkipLink("#main-content")  # Place at top of page
    """
    
    def __init__(self, target: str = "#main", text: str = "Skip to main content"):
        self.target = target
        self.text = text
    
    def render(self) -> str:
        return f'''
        <a href="{self.target}" 
           class="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-lg focus:outline-none">
            {self.text}
        </a>
        '''
    
    def __str__(self):
        return self.render()


class VisuallyHidden:
    """
    Visually hidden but accessible to screen readers.
    
    Usage:
        VisuallyHidden("Additional context for screen readers")
    """
    
    def __init__(self, text: str):
        self.text = text
    
    def render(self) -> str:
        return f'<span class="sr-only">{self.text}</span>'
    
    def __str__(self):
        return self.render()


class LiveRegion:
    """
    Live region for announcing updates to screen readers.
    
    Usage:
        LiveRegion(id="status", mode="polite")  # Place in layout
        # Then update content dynamically
    """
    
    def __init__(
        self,
        id: str = "live-region",
        mode: str = "polite",  # 'polite', 'assertive'
        atomic: bool = True,
        className: str = "",
    ):
        self.id = id
        self.mode = mode
        self.atomic = atomic
        self.className = className
    
    def render(self) -> str:
        atomic = "true" if self.atomic else "false"
        return f'''
        <div id="{self.id}" 
             class="sr-only {self.className}"
             role="status"
             aria-live="{self.mode}"
             aria-atomic="{atomic}">
        </div>
        
        <script>
            window.PyxA11y = window.PyxA11y || {{
                announce: function(message, regionId = '{self.id}') {{
                    const region = document.getElementById(regionId);
                    if (region) {{
                        region.textContent = '';
                        setTimeout(() => {{
                            region.textContent = message;
                        }}, 100);
                    }}
                }},
                
                announcePolite: function(message) {{
                    this.announce(message);
                }},
                
                announceAssertive: function(message) {{
                    const region = document.getElementById('{self.id}');
                    if (region) {{
                        region.setAttribute('aria-live', 'assertive');
                        this.announce(message);
                        setTimeout(() => {{
                            region.setAttribute('aria-live', 'polite');
                        }}, 1000);
                    }}
                }}
            }};
        </script>
        '''
    
    def __str__(self):
        return self.render()


class A11yStyles:
    """
    CSS utilities for accessibility.
    Include in your layout.
    """
    
    @staticmethod
    def render() -> str:
        return '''
        <style>
            /* Screen reader only */
            .sr-only {
                position: absolute;
                width: 1px;
                height: 1px;
                padding: 0;
                margin: -1px;
                overflow: hidden;
                clip: rect(0, 0, 0, 0);
                white-space: nowrap;
                border-width: 0;
            }
            
            /* Focus visible styles */
            .focus-visible:focus {
                outline: 2px solid #3b82f6;
                outline-offset: 2px;
            }
            
            /* Reduce motion for users who prefer it */
            @media (prefers-reduced-motion: reduce) {
                *, *::before, *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            }
            
            /* High contrast mode */
            @media (prefers-contrast: high) {
                .pyx-button {
                    border: 2px solid currentColor;
                }
            }
            
            /* Dark mode - higher contrast */
            .dark .text-gray-500 {
                color: #9ca3af;
            }
        </style>
        '''
    
    def __str__(self):
        return self.render()


class KeyboardNav:
    """
    Add keyboard navigation to a list/group.
    
    Usage:
        KeyboardNav(
            ui.div([item1, item2, item3]),
            selector=".item",
            orientation="vertical"
        )
    """
    
    def __init__(
        self,
        content,
        selector: str = "[role='menuitem'], [role='option'], button",
        orientation: str = "vertical",  # 'vertical', 'horizontal', 'grid'
        wrap: bool = True,
        className: str = "",
    ):
        self.content = content
        self.selector = selector
        self.orientation = orientation
        self.wrap = wrap
        self.className = className
        self._id = f"keyboard-nav-{uuid.uuid4().hex[:8]}"
    
    def render(self) -> str:
        content_html = self.content.render() if hasattr(self.content, 'render') else str(self.content)
        
        if self.orientation == "vertical":
            prev_key = "ArrowUp"
            next_key = "ArrowDown"
        elif self.orientation == "horizontal":
            prev_key = "ArrowLeft"
            next_key = "ArrowRight"
        else:  # grid
            prev_key = "ArrowUp"
            next_key = "ArrowDown"
        
        return f'''
        <div id="{self._id}" class="keyboard-nav {self.className}">
            {content_html}
        </div>
        
        <script>
            (function() {{
                const container = document.getElementById('{self._id}');
                const selector = '{self.selector}';
                
                container.addEventListener('keydown', function(e) {{
                    const items = Array.from(container.querySelectorAll(selector));
                    if (items.length === 0) return;
                    
                    const currentIndex = items.indexOf(document.activeElement);
                    let newIndex = currentIndex;
                    
                    switch(e.key) {{
                        case '{prev_key}':
                            e.preventDefault();
                            newIndex = currentIndex > 0 ? currentIndex - 1 : ({'items.length - 1' if self.wrap else 'currentIndex'});
                            break;
                        case '{next_key}':
                            e.preventDefault();
                            newIndex = currentIndex < items.length - 1 ? currentIndex + 1 : ({'0' if self.wrap else 'currentIndex'});
                            break;
                        case 'Home':
                            e.preventDefault();
                            newIndex = 0;
                            break;
                        case 'End':
                            e.preventDefault();
                            newIndex = items.length - 1;
                            break;
                    }}
                    
                    if (newIndex !== currentIndex && items[newIndex]) {{
                        items[newIndex].focus();
                    }}
                }});
            }})();
        </script>
        '''
    
    def __str__(self):
        return self.render()
