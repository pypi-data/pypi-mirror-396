"""
PyX Suspense System
Loading states, Error boundaries, and Streaming.
"""
import asyncio
import uuid
from typing import Callable, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class SuspenseConfig:
    """Configuration for suspense behavior"""
    fallback: Any = None  # Loading component
    error_fallback: Any = None  # Error component
    timeout: int = 10000  # Timeout in ms
    retry: int = 0  # Number of retries
    delay: int = 0  # Minimum loading time (avoid flash)


class Suspense:
    """
    Suspense wrapper for async content with loading states.
    
    Usage:
        Suspense(
            content=AsyncDataComponent(),
            loading=ui.skeleton(),
            error=ErrorMessage()
        )
        
    Or with decorator:
        @suspense(loading=ui.spinner())
        async def my_page():
            data = await fetch_data()
            return ui.div(data)
    """
    
    def __init__(
        self,
        content: Any,
        loading: Any = None,
        error: Any = None,
        timeout: int = 10000,
        delay: int = 0,
        className: str = "",
    ):
        self.content = content
        self.loading = loading
        self.error = error
        self.timeout = timeout
        self.delay = delay
        self.className = className
        self._id = f"suspense-{uuid.uuid4().hex[:8]}"
    
    def render(self) -> str:
        # Default loading state
        if self.loading is None:
            loading_html = '''
                <div class="flex items-center justify-center p-8">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
            '''
        else:
            loading_html = self.loading.render() if hasattr(self.loading, 'render') else str(self.loading)
        
        # Default error state
        if self.error is None:
            error_html = '''
                <div class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                    <p class="font-medium">Something went wrong</p>
                    <button onclick="location.reload()" class="mt-2 text-sm underline">Try again</button>
                </div>
            '''
        else:
            error_html = self.error.render() if hasattr(self.error, 'render') else str(self.error)
        
        # Content
        content_html = self.content.render() if hasattr(self.content, 'render') else str(self.content)
        
        return f'''
        <div id="{self._id}" class="suspense-boundary {self.className}" data-state="loading">
            <div class="suspense-loading">{loading_html}</div>
            <div class="suspense-content hidden">{content_html}</div>
            <div class="suspense-error hidden">{error_html}</div>
        </div>
        
        <script>
            (function() {{
                const container = document.getElementById('{self._id}');
                const loadingEl = container.querySelector('.suspense-loading');
                const contentEl = container.querySelector('.suspense-content');
                const errorEl = container.querySelector('.suspense-error');
                
                // Simulate async loading (in real app, this would be data fetching)
                const minDelay = {self.delay};
                const timeout = {self.timeout};
                
                const startTime = Date.now();
                
                // Check if content has loaded
                const checkReady = () => {{
                    const elapsed = Date.now() - startTime;
                    
                    // Minimum delay
                    if (elapsed < minDelay) {{
                        setTimeout(checkReady, minDelay - elapsed);
                        return;
                    }}
                    
                    // Show content
                    loadingEl.classList.add('hidden');
                    contentEl.classList.remove('hidden');
                    container.dataset.state = 'ready';
                }};
                
                // Start check after brief delay (let content render)
                setTimeout(checkReady, 100);
                
                // Timeout handler
                setTimeout(() => {{
                    if (container.dataset.state === 'loading') {{
                        loadingEl.classList.add('hidden');
                        errorEl.classList.remove('hidden');
                        container.dataset.state = 'error';
                    }}
                }}, timeout);
            }})();
        </script>
        '''
    
    def __str__(self):
        return self.render()


class ErrorBoundary:
    """
    Error boundary for graceful error handling.
    
    Usage:
        ErrorBoundary(
            content=RiskyComponent(),
            fallback=ErrorMessage("Something went wrong")
        )
    """
    
    def __init__(
        self,
        content: Any,
        fallback: Any = None,
        on_error: Callable = None,
        className: str = "",
    ):
        self.content = content
        self.fallback = fallback
        self.on_error = on_error
        self.className = className
        self._id = f"error-boundary-{uuid.uuid4().hex[:8]}"
    
    def render(self) -> str:
        # Default fallback
        if self.fallback is None:
            fallback_html = '''
                <div class="p-6 bg-red-50 border border-red-200 rounded-lg text-center">
                    <svg class="w-12 h-12 mx-auto text-red-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                    </svg>
                    <p class="text-red-700 font-medium">An error occurred</p>
                    <p class="text-red-500 text-sm mt-1 error-message"></p>
                    <button onclick="location.reload()" class="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
                        Reload Page
                    </button>
                </div>
            '''
        else:
            fallback_html = self.fallback.render() if hasattr(self.fallback, 'render') else str(self.fallback)
        
        try:
            content_html = self.content.render() if hasattr(self.content, 'render') else str(self.content)
            has_error = False
        except Exception as e:
            content_html = ""
            has_error = True
            if self.on_error:
                self.on_error(e)
        
        return f'''
        <div id="{self._id}" class="error-boundary {self.className}">
            <div class="error-content {'hidden' if has_error else ''}">{content_html}</div>
            <div class="error-fallback {'hidden' if not has_error else ''}">{fallback_html}</div>
        </div>
        
        <script>
            window.addEventListener('error', function(event) {{
                const container = document.getElementById('{self._id}');
                if (container && event.target.closest && event.target.closest('#{self._id}')) {{
                    container.querySelector('.error-content').classList.add('hidden');
                    container.querySelector('.error-fallback').classList.remove('hidden');
                    const msgEl = container.querySelector('.error-message');
                    if (msgEl) msgEl.textContent = event.message;
                }}
            }});
        </script>
        '''
    
    def __str__(self):
        return self.render()


class Loading:
    """
    Loading component with various styles.
    
    Usage:
        Loading()  # Default spinner
        Loading(variant="skeleton", lines=3)
        Loading(variant="dots")
        Loading(variant="pulse")
    """
    
    def __init__(
        self,
        variant: str = "spinner",  # 'spinner', 'skeleton', 'dots', 'pulse', 'bar'
        size: str = "md",  # 'sm', 'md', 'lg'
        lines: int = 3,  # For skeleton
        text: str = None,  # Loading text
        className: str = "",
    ):
        self.variant = variant
        self.size = size
        self.lines = lines
        self.text = text
        self.className = className
    
    def render(self) -> str:
        sizes = {
            "sm": "h-4 w-4",
            "md": "h-8 w-8",
            "lg": "h-12 w-12",
        }
        size_class = sizes.get(self.size, sizes["md"])
        
        if self.variant == "spinner":
            return f'''
            <div class="flex flex-col items-center justify-center gap-2 {self.className}">
                <div class="animate-spin rounded-full {size_class} border-b-2 border-blue-600"></div>
                {f'<p class="text-sm text-gray-500">{self.text}</p>' if self.text else ''}
            </div>
            '''
        
        elif self.variant == "skeleton":
            lines_html = ""
            for i in range(self.lines):
                width = "100%" if i == 0 else f"{80 - i * 15}%"
                lines_html += f'<div class="h-4 bg-gray-200 rounded animate-pulse" style="width: {width}"></div>'
            return f'''
            <div class="space-y-3 {self.className}">
                {lines_html}
            </div>
            '''
        
        elif self.variant == "dots":
            return f'''
            <div class="flex items-center gap-1 {self.className}">
                <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
            </div>
            '''
        
        elif self.variant == "pulse":
            return f'''
            <div class="animate-pulse {self.className}">
                <div class="rounded-lg bg-gray-200 {size_class}"></div>
            </div>
            '''
        
        elif self.variant == "bar":
            return f'''
            <div class="w-full h-1 bg-gray-200 rounded overflow-hidden {self.className}">
                <div class="h-full bg-blue-600 rounded animate-pulse" style="width: 30%; animation: loading-bar 1.5s infinite"></div>
            </div>
            <style>
                @keyframes loading-bar {{
                    0% {{ transform: translateX(-100%); }}
                    100% {{ transform: translateX(400%); }}
                }}
            </style>
            '''
        
        return f'<div class="animate-pulse {self.className}">Loading...</div>'
    
    def __str__(self):
        return self.render()


class StreamingResponse:
    """
    Streaming/Progressive rendering support.
    
    Usage:
        @streaming
        async def my_page():
            yield Header()  # Sent immediately
            
            data = await fetch_data()  # Takes time
            yield DataTable(data)  # Sent when ready
            
            yield Footer()  # Sent after
    """
    
    def __init__(self, generator: Callable):
        self.generator = generator
    
    async def stream(self):
        """Generate streaming HTML chunks"""
        # Send opening
        yield "<!DOCTYPE html><html><head>"
        yield '<script src="https://cdn.tailwindcss.com"></script>'
        yield "</head><body>"
        
        # Stream content
        async for chunk in self.generator():
            if hasattr(chunk, 'render'):
                yield chunk.render()
            else:
                yield str(chunk)
        
        # Close
        yield "</body></html>"


def suspense(loading=None, error=None, timeout=10000):
    """
    Decorator to add suspense to a page/component.
    
    Usage:
        @suspense(loading=Skeleton())
        async def my_page():
            data = await fetch_data()
            return DataView(data)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            content = func(*args, **kwargs)
            return Suspense(
                content=content,
                loading=loading,
                error=error,
                timeout=timeout
            )
        return wrapper
    return decorator


def error_boundary(fallback=None, on_error=None):
    """
    Decorator to add error boundary to a component.
    
    Usage:
        @error_boundary(fallback=ErrorMessage())
        def risky_component():
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            content = func(*args, **kwargs)
            return ErrorBoundary(
                content=content,
                fallback=fallback,
                on_error=on_error
            )
        return wrapper
    return decorator
