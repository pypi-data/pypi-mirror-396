"""
PyX Reactive System
Core reactive primitives for building reactive UIs.
"""
import json
import uuid
from typing import Any, Callable, List, TypeVar, Generic, Union

T = TypeVar('T')


class ReactiveValue(Generic[T]):
    """
    A reactive wrapper that tracks its bindings and triggers updates.
    
    When the value changes, all bound UI elements are automatically updated
    via WebSocket.
    """
    
    _all_reactives: dict = {}  # Global registry: {id: ReactiveValue}
    
    def __init__(self, initial_value: T, name: str = None):
        self._value = initial_value
        self._id = name or f"rv-{uuid.uuid4().hex[:8]}"
        self._bindings: List[str] = []  # List of element IDs bound to this value
        ReactiveValue._all_reactives[self._id] = self
    
    @property
    def value(self) -> T:
        return self._value
    
    @value.setter
    def value(self, new_value: T):
        if self._value != new_value:
            self._value = new_value
            self._notify()
    
    def set(self, new_value: T):
        """Explicit setter method"""
        self.value = new_value
    
    def _notify(self):
        """Notify all bound elements of the change"""
        from .state import manager
        import asyncio
        
        # Prepare update payload
        content = self._render_value()
        
        # Broadcast to all bound elements
        for element_id in self._bindings:
            try:
                asyncio.create_task(manager.broadcast(element_id, content))
            except:
                pass  # Handle case where no event loop
    
    def _render_value(self) -> str:
        """Convert value to string for display"""
        if isinstance(self._value, bool):
            return "true" if self._value else "false"
        elif isinstance(self._value, (list, dict)):
            return json.dumps(self._value)
        return str(self._value)
    
    def bind(self, element_id: str):
        """Register an element ID as bound to this reactive value"""
        if element_id not in self._bindings:
            self._bindings.append(element_id)
        return self
    
    def __str__(self):
        return str(self._value)
    
    def __repr__(self):
        return f"ReactiveValue({self._value})"
    
    # Arithmetic operations for reactive numbers
    def __add__(self, other):
        other_val = other.value if isinstance(other, ReactiveValue) else other
        return self._value + other_val
    
    def __sub__(self, other):
        other_val = other.value if isinstance(other, ReactiveValue) else other
        return self._value - other_val
    
    def __mul__(self, other):
        other_val = other.value if isinstance(other, ReactiveValue) else other
        return self._value * other_val
    
    # Comparison for conditionals
    def __eq__(self, other):
        other_val = other.value if isinstance(other, ReactiveValue) else other
        return self._value == other_val
    
    def __lt__(self, other):
        other_val = other.value if isinstance(other, ReactiveValue) else other
        return self._value < other_val
    
    def __gt__(self, other):
        other_val = other.value if isinstance(other, ReactiveValue) else other
        return self._value > other_val
    
    def __bool__(self):
        return bool(self._value)


# ==========================================
# REACTIVE CONTROL FLOW
# ==========================================

class Cond:
    """
    Conditional rendering based on reactive value.
    
    Usage:
        Cond(
            UserState.is_logged_in,
            ui.div("Welcome!"),
            ui.div("Please login")
        )
    """
    
    def __init__(self, condition, true_component, false_component=None):
        self.condition = condition
        self.true_component = true_component
        self.false_component = false_component
        self._id = f"cond-{uuid.uuid4().hex[:8]}"
        
    def render(self) -> str:
        # Evaluate condition
        cond_val = self.condition
        if isinstance(cond_val, ReactiveValue):
            cond_val = cond_val.value
        elif callable(cond_val):
            cond_val = cond_val()
            
        if cond_val:
            content = self.true_component
        else:
            content = self.false_component
            
        if content is None:
            return ""
            
        inner = content.render() if hasattr(content, 'render') else str(content)
        
        # Wrap in container for reactive updates
        return f'<div id="{self._id}" data-pyx-cond="true">{inner}</div>'
    
    def __str__(self):
        return self.render()


class ForEach:
    """
    Render a list of items reactively.
    
    Usage:
        ForEach(
            ProductState.products,
            lambda product: ui.div(product["name"])
        )
    """
    
    def __init__(self, items, render_fn: Callable[[Any], Any], key: str = "id"):
        self.items = items
        self.render_fn = render_fn
        self.key = key
        self._id = f"foreach-{uuid.uuid4().hex[:8]}"
        
    def render(self) -> str:
        # Get items value
        items_val = self.items
        if isinstance(items_val, ReactiveValue):
            items_val = items_val.value
        elif callable(items_val):
            items_val = items_val()
            
        if not items_val:
            return f'<div id="{self._id}" data-pyx-foreach="true"></div>'
        
        # Render each item
        rendered_items = []
        for item in items_val:
            item_content = self.render_fn(item)
            item_html = item_content.render() if hasattr(item_content, 'render') else str(item_content)
            
            # Add key for efficient updates
            item_key = item.get(self.key, id(item)) if isinstance(item, dict) else id(item)
            rendered_items.append(f'<div data-key="{item_key}">{item_html}</div>')
        
        return f'<div id="{self._id}" data-pyx-foreach="true">{"".join(rendered_items)}</div>'
    
    def __str__(self):
        return self.render()


class Match:
    """
    Pattern matching / switch-case for reactive rendering.
    
    Usage:
        Match(
            PageState.current_tab,
            {
                "home": ui.div("Home Page"),
                "settings": ui.div("Settings Page"),
                "profile": ui.div("Profile Page"),
            },
            default=ui.div("404 Not Found")
        )
    """
    
    def __init__(self, value, cases: dict, default=None):
        self.value = value
        self.cases = cases
        self.default = default
        self._id = f"match-{uuid.uuid4().hex[:8]}"
        
    def render(self) -> str:
        # Get value
        val = self.value
        if isinstance(val, ReactiveValue):
            val = val.value
        elif callable(val):
            val = val()
            
        # Find matching case
        component = self.cases.get(val, self.default)
        
        if component is None:
            return f'<div id="{self._id}" data-pyx-match="true"></div>'
            
        inner = component.render() if hasattr(component, 'render') else str(component)
        return f'<div id="{self._id}" data-pyx-match="true">{inner}</div>'
    
    def __str__(self):
        return self.render()


# ==========================================
# REACTIVE TEXT BINDING
# ==========================================

class ReactiveText:
    """
    A text node that automatically updates when the reactive value changes.
    
    Usage:
        ReactiveText(CounterState.count)
        ReactiveText(lambda: f"Count: {CounterState.count}")
    """
    
    def __init__(self, value_or_fn):
        self.value_or_fn = value_or_fn
        self._id = f"rt-{uuid.uuid4().hex[:8]}"
        
        # Register binding if it's a ReactiveValue
        if isinstance(value_or_fn, ReactiveValue):
            value_or_fn.bind(self._id)
    
    def render(self) -> str:
        if isinstance(self.value_or_fn, ReactiveValue):
            content = str(self.value_or_fn.value)
        elif callable(self.value_or_fn):
            content = str(self.value_or_fn())
        else:
            content = str(self.value_or_fn)
            
        return f'<span id="{self._id}" data-pyx-reactive="true">{content}</span>'
    
    def __str__(self):
        return self.render()


# ==========================================
# CONVENIENCE FUNCTIONS
# ==========================================

def rx(value) -> ReactiveValue:
    """Create a new reactive value."""
    return ReactiveValue(value)

def cond(condition, true_comp, false_comp=None) -> Cond:
    """Conditional rendering."""
    return Cond(condition, true_comp, false_comp)

def foreach(items, render_fn, key="id") -> ForEach:
    """List rendering."""
    return ForEach(items, render_fn, key)

def match(value, cases, default=None) -> Match:
    """Pattern matching."""
    return Match(value, cases, default)

def text(value) -> ReactiveText:
    """Reactive text node."""
    return ReactiveText(value)
