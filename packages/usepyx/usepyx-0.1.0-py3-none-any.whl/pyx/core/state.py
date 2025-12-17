"""
PyX State Management System
Inspired by Reflex's State architecture.

This module provides the core State class that enables:
- Reactive state variables
- Auto-generated setters
- Event handlers that return UI actions
- Per-session state isolation
"""

from typing import Any, Dict, Optional, Callable, Type, get_type_hints
from dataclasses import dataclass, field
import inspect


@dataclass
class Action:
    """Base class for UI actions returned by event handlers."""
    pass


@dataclass
class RedirectAction(Action):
    """Navigate to a different URL."""
    url: str
    
    def to_dict(self) -> dict:
        return {"type": "navigate", "url": self.url}


@dataclass
class AlertAction(Action):
    """Show a browser alert."""
    message: str
    
    def to_dict(self) -> dict:
        return {"type": "alert", "message": self.message}


@dataclass
class ToastAction(Action):
    """Show a toast notification."""
    message: str
    variant: str = "info"  # info, success, warning, error
    duration: int = 3000
    
    def to_dict(self) -> dict:
        return {
            "type": "toast",
            "message": self.message,
            "variant": self.variant,
            "duration": self.duration
        }


@dataclass  
class RefreshAction(Action):
    """Re-render the current page."""
    
    def to_dict(self) -> dict:
        return {"type": "refresh"}


# Convenience functions for creating actions
def redirect(url: str) -> RedirectAction:
    """Create a redirect action."""
    return RedirectAction(url=url)


def alert(message: str) -> AlertAction:
    """Create an alert action."""
    return AlertAction(message=message)


def toast(message: str, variant: str = "info", duration: int = 3000) -> ToastAction:
    """Create a toast action."""
    return ToastAction(message=message, variant=variant, duration=duration)


def refresh() -> RefreshAction:
    """Create a refresh action."""
    return RefreshAction()


# =============================================================================
# COMPUTED VARS
# =============================================================================

class ComputedVar:
    """
    Descriptor for computed (derived) state variables.
    
    Computed vars are automatically recalculated when accessed,
    based on other state variables.
    
    Usage:
        class CounterState(State):
            count: int = 0
            
            @var
            def double_count(self) -> int:
                return self.count * 2
            
            @var  
            def is_positive(self) -> bool:
                return self.count > 0
    """
    
    def __init__(self, func: Callable):
        self.func = func
        self.name = func.__name__
        self.__doc__ = func.__doc__
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        # Recompute value each time it's accessed
        return self.func(obj)
    
    def __set__(self, obj, value):
        raise AttributeError(
            f"Cannot set computed var '{self.name}'. "
            "Computed vars are read-only and derived from other state."
        )


def var(func: Callable) -> ComputedVar:
    """
    Decorator to create a computed (derived) state variable.
    
    Computed vars are automatically recalculated when accessed.
    They cannot be set directly - they derive their value from other state.
    
    Usage:
        from pyx import State, var
        
        class CartState(State):
            items: list = []
            tax_rate: float = 0.1
            
            @var
            def subtotal(self) -> float:
                return sum(item.price for item in self.items)
            
            @var
            def tax(self) -> float:
                return self.subtotal * self.tax_rate
            
            @var
            def total(self) -> float:
                return self.subtotal + self.tax
            
            @var
            def item_count(self) -> int:
                return len(self.items)
    
    Returns:
        ComputedVar: A descriptor that computes the value on access.
    """
    return ComputedVar(func)


# Alias for consistency with Reflex naming
computed = var


class StateMeta(type):
    """
    Metaclass for State that auto-generates setters for typed variables.
    """
    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        cls = super().__new__(mcs, name, bases, namespace)
        
        # Get type hints for the class
        hints = {}
        try:
            hints = get_type_hints(cls)
        except Exception:
            pass
        
        # For each typed attribute, create a setter if it doesn't exist
        for var_name, var_type in hints.items():
            if var_name.startswith('_'):
                continue
            
            setter_name = f"set_{var_name}"
            
            # Only create setter if not already defined
            if not hasattr(cls, setter_name):
                def make_setter(attr_name):
                    def setter(self, value):
                        setattr(self, attr_name, value)
                    return setter
                
                setattr(cls, setter_name, make_setter(var_name))
        
        return cls


class State(metaclass=StateMeta):
    """
    Base State class for PyX applications.
    
    Usage:
        class AuthState(State):
            username: str = ""
            password: str = ""
            logged_in: bool = False
            
            def login(self):
                if self.username == "admin" and self.password == "password":
                    self.logged_in = True
                    return redirect("/dashboard")
                else:
                    return alert("Invalid credentials")
    
    Features:
        - Type-hinted variables become reactive state
        - Auto-generated setters (e.g., `set_username`)
        - Event handlers can return Actions (redirect, alert, toast)
    """
    
    # Internal tracking
    _vars: Dict[str, Any] = {}
    _session_id: Optional[str] = None
    
    def __init__(self, session_id: Optional[str] = None):
        """Initialize state, optionally with a session ID for isolation."""
        self._session_id = session_id
        self._init_vars()
    
    def _init_vars(self):
        """Initialize all typed variables with their default values."""
        hints = get_type_hints(self.__class__)
        for var_name, var_type in hints.items():
            if var_name.startswith('_'):
                continue
            # Get default value from class if exists
            default = getattr(self.__class__, var_name, None)
            setattr(self, var_name, default)
    
    def get_vars(self) -> Dict[str, Any]:
        """Get all state variables as a dictionary."""
        hints = get_type_hints(self.__class__)
        return {
            var_name: getattr(self, var_name, None)
            for var_name in hints
            if not var_name.startswith('_')
        }
    
    def reset(self):
        """Reset all state variables to their defaults."""
        self._init_vars()


# Session Manager for per-session state isolation
class StateManager:
    """
    Manages State instances per session.
    
    Each browser tab/session gets its own State instance.
    """
    
    _instances: Dict[str, Dict[Type[State], State]] = {}
    _state_classes: Dict[str, Type[State]] = {}
    
    @classmethod
    def register(cls, state_class: Type[State]):
        """Register a State class for the application."""
        cls._state_classes[state_class.__name__] = state_class
    
    @classmethod
    def get(cls, session_id: str, state_class: Type[State]) -> State:
        """Get or create a State instance for a session."""
        if session_id not in cls._instances:
            cls._instances[session_id] = {}
        
        if state_class not in cls._instances[session_id]:
            cls._instances[session_id][state_class] = state_class(session_id=session_id)
        
        return cls._instances[session_id][state_class]
    
    @classmethod
    def clear(cls, session_id: str):
        """Clear all state for a session (e.g., on logout)."""
        if session_id in cls._instances:
            del cls._instances[session_id]


# Export convenience
__all__ = [
    'State',
    'StateManager',
    'Action',
    'RedirectAction',
    'AlertAction',
    'ToastAction',
    'RefreshAction',
    'redirect',
    'alert',
    'toast',
    'refresh',
    'var',
    'computed',
    'ComputedVar',
]
