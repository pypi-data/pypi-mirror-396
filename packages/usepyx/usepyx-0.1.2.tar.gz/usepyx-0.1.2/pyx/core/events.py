import asyncio
import inspect
from typing import Callable, Any, Dict, Generator
from functools import wraps


class EventManager:
    """
    PyX Event Engine.
    Handles registration and execution of event handlers with advanced features.
    """
    _handlers: Dict[str, Callable] = {}
    _background_handlers: Dict[str, bool] = {}  # Track which handlers run in background

    @classmethod
    def register(cls, func: Callable, background: bool = False) -> str:
        """
        Register a function as an event handler.
        
        Args:
            func: The handler function
            background: If True, runs in a background thread (non-blocking)
        """
        name = func.__name__
        cls._handlers[name] = func
        if background:
            cls._background_handlers[name] = True
        return name

    @classmethod
    def get_handler(cls, name: str) -> Callable:
        """Get handler function by name"""
        return cls._handlers.get(name)

    @classmethod
    def is_background(cls, name: str) -> bool:
        """Check if handler should run in background"""
        return cls._background_handlers.get(name, False)

    @classmethod
    def clear(cls):
        cls._handlers = {}
        cls._background_handlers = {}

    @classmethod
    async def execute(cls, name: str, data: Dict[str, Any] = None, websocket=None):
        """
        Execute an event handler with optional data.
        Supports:
        - Regular functions
        - Async functions
        - Generator functions (yield events)
        - Background execution
        
        Args:
            name: Handler name
            data: Event data (form values, etc.)
            websocket: WebSocket connection for sending updates
        """
        import json
        
        func = cls.get_handler(name)
        if not func:
            print(f"[PyX Events] Handler not found: {name}")
            return None
        
        # Prepare arguments based on function signature
        sig = inspect.signature(func)
        kwargs = {}
        
        # Smart argument injection
        if data:
            for param_name in sig.parameters:
                if param_name in data:
                    kwargs[param_name] = data[param_name]
                elif param_name == "data":
                    # Pass entire data dict if param named 'data'
                    kwargs["data"] = data
        
        # Execute based on handler type
        try:
            # Check if it's a generator (yield events)
            if inspect.isgeneratorfunction(func):
                # Yield Events: Stream partial updates
                for update in func(**kwargs):
                    if websocket and update:
                        await cls._send_update(websocket, update)
                return
            
            # Check if async
            if asyncio.iscoroutinefunction(func):
                result = await func(**kwargs)
            else:
                # Check if should run in background
                if cls.is_background(name):
                    # Run in thread pool
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, lambda: func(**kwargs))
                else:
                    result = func(**kwargs)
            
            # Handle result (could be a JS action)
            if result and websocket:
                await cls._send_update(websocket, result)
                
            return result
            
        except Exception as e:
            print(f"[PyX Events] Error in {name}: {e}")
            import traceback
            traceback.print_exc()
            return None

    @classmethod
    async def _send_update(cls, websocket, update):
        """Send update to client via WebSocket"""
        import json
        
        # Handle different update types
        if hasattr(update, 'code'):
            # It's a JS action
            await websocket.send_text(json.dumps({
                "type": "js_eval",
                "code": str(update)
            }))
        elif isinstance(update, dict):
            await websocket.send_text(json.dumps(update))
        elif isinstance(update, str):
            # Assume it's HTML to update
            await websocket.send_text(json.dumps({
                "type": "update",
                "content": update
            }))


# ==========================================
# DECORATORS
# ==========================================

def background(func: Callable) -> Callable:
    """
    Decorator to mark a handler as background task.
    The function will run in a thread pool without blocking UI.
    
    Usage:
        @background
        def send_email(to, subject):
            # This runs in background
            ...
    """
    EventManager.register(func, background=True)
    return func


def event(func: Callable) -> Callable:
    """
    Decorator to register a function as an event handler.
    
    Usage:
        @event
        def handle_click():
            ...
    """
    EventManager.register(func)
    return func
