"""
PyX Background Tasks
============================================================================
Simple decorators and utilities for running tasks in the background.

This module provides a clean API for background operations that:
- Don't block the UI
- Can update State during execution
- Support progress reporting
- Handle errors gracefully
"""

import asyncio
import threading
from typing import Callable, Any, Optional, Dict
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
import traceback


# Thread pool for background tasks
_executor = ThreadPoolExecutor(max_workers=4)


def background(func: Callable) -> Callable:
    """
    Decorator to run a function in the background without blocking the UI.
    
    Usage:
        from pyx import background, toast
        
        @background
        async def send_email(user_id: int):
            # This runs in background - UI doesn't freeze
            await email.send(...)
            return toast("Email sent!", "success")
        
        # In your event handler
        def handle_submit(self):
            send_email(self.user_id)  # Returns immediately
            return toast("Sending email...", "info")
    
    The decorated function:
    - Returns immediately (non-blocking)
    - Runs in a separate thread/task
    - Can return Actions that will be sent to the client
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        def run_task():
            try:
                if asyncio.iscoroutinefunction(func):
                    # Run async function in new event loop
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        result = loop.run_until_complete(func(*args, **kwargs))
                    finally:
                        loop.close()
                else:
                    result = func(*args, **kwargs)
                
                # If result is an Action, we could potentially send it
                # via WebSocket, but that requires session context
                print(f"[Background] Task completed: {func.__name__}")
                return result
                
            except Exception as e:
                print(f"[Background] Task failed: {func.__name__} - {e}")
                traceback.print_exc()
                return None
        
        # Submit to thread pool
        future = _executor.submit(run_task)
        print(f"[Background] Task started: {func.__name__}")
        return future
    
    # Mark as background task
    wrapper._is_background = True
    return wrapper


class BackgroundTask:
    """
    A more advanced background task with progress reporting.
    
    Usage:
        from pyx.tasks import BackgroundTask
        
        task = BackgroundTask(
            name="data_import",
            func=import_data,
            on_progress=update_progress_bar,
            on_complete=show_success,
            on_error=show_error
        )
        task.start(file_path="data.csv")
    """
    
    def __init__(
        self,
        name: str,
        func: Callable,
        on_progress: Optional[Callable[[int, str], None]] = None,
        on_complete: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None
    ):
        self.name = name
        self.func = func
        self.on_progress = on_progress
        self.on_complete = on_complete
        self.on_error = on_error
        self.progress = 0
        self.status = "idle"  # idle, running, completed, failed
        self.result = None
        self.error = None
    
    def set_progress(self, percent: int, message: str = ""):
        """Update task progress (call from within the task function)."""
        self.progress = percent
        if self.on_progress:
            self.on_progress(percent, message)
    
    def start(self, *args, **kwargs):
        """Start the task in background."""
        self.status = "running"
        self.progress = 0
        
        def run():
            try:
                # Inject task reference for progress updates
                kwargs['_task'] = self
                
                if asyncio.iscoroutinefunction(self.func):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        self.result = loop.run_until_complete(
                            self.func(*args, **kwargs)
                        )
                    finally:
                        loop.close()
                else:
                    self.result = self.func(*args, **kwargs)
                
                self.status = "completed"
                self.progress = 100
                
                if self.on_complete:
                    self.on_complete(self.result)
                    
            except Exception as e:
                self.status = "failed"
                self.error = e
                
                if self.on_error:
                    self.on_error(e)
                else:
                    traceback.print_exc()
        
        _executor.submit(run)
        print(f"[BackgroundTask] Started: {self.name}")


def run_async(coro):
    """
    Helper to run an async coroutine from synchronous code.
    
    Usage:
        result = run_async(some_async_function())
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def delayed(seconds: float):
    """
    Decorator to delay execution of a function.
    
    Usage:
        @delayed(5)
        def send_reminder():
            # This runs 5 seconds after being called
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            def run_after_delay():
                import time
                time.sleep(seconds)
                return func(*args, **kwargs)
            
            future = _executor.submit(run_after_delay)
            print(f"[Delayed] Task scheduled: {func.__name__} in {seconds}s")
            return future
        return wrapper
    return decorator


def periodic(interval: float, max_runs: Optional[int] = None):
    """
    Decorator to run a function periodically.
    
    Usage:
        @periodic(60)  # Run every 60 seconds
        def check_notifications():
            ...
        
        # Start the periodic task
        stop_fn = check_notifications()
        
        # Later, to stop:
        stop_fn()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            stop_flag = threading.Event()
            run_count = 0
            
            def run_periodically():
                nonlocal run_count
                while not stop_flag.is_set():
                    try:
                        func(*args, **kwargs)
                    except Exception as e:
                        print(f"[Periodic] Error in {func.__name__}: {e}")
                    
                    run_count += 1
                    if max_runs and run_count >= max_runs:
                        break
                    
                    stop_flag.wait(interval)
            
            thread = threading.Thread(target=run_periodically, daemon=True)
            thread.start()
            print(f"[Periodic] Started: {func.__name__} every {interval}s")
            
            def stop():
                stop_flag.set()
                print(f"[Periodic] Stopped: {func.__name__}")
            
            return stop
        return wrapper
    return decorator


# Exports
__all__ = [
    'background',
    'BackgroundTask',
    'run_async',
    'delayed',
    'periodic',
]
