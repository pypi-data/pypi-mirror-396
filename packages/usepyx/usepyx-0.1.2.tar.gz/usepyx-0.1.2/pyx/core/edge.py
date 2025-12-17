"""
PyX Edge Runtime
Edge-first deployment and edge functions support.
"""
import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from functools import wraps


@dataclass
class EdgeConfig:
    """Edge runtime configuration"""
    runtime: str = "edge"  # 'edge' or 'nodejs'
    regions: List[str] = None  # ['iad1', 'sfo1', 'hnd1']
    memory: int = 128  # MB
    timeout: int = 30  # seconds
    
    def __post_init__(self):
        if self.regions is None:
            self.regions = ["auto"]


class EdgeFunction:
    """
    Edge Function wrapper.
    Runs on edge servers (CDN) close to users.
    
    Usage:
        @edge
        def my_handler(request):
            return {"message": "Hello from edge!"}
        
        @edge(regions=["iad1", "hnd1"])
        def geo_handler(request):
            return {"region": request.geo.region}
    """
    
    def __init__(
        self,
        handler: Callable,
        config: EdgeConfig = None,
    ):
        self.handler = handler
        self.config = config or EdgeConfig()
        self._name = handler.__name__
    
    async def __call__(self, request):
        """Execute the edge function"""
        # Add edge context to request
        if not hasattr(request, 'edge'):
            request.edge = EdgeContext(request)
        
        # Execute handler
        if asyncio.iscoroutinefunction(self.handler):
            return await self.handler(request)
        return self.handler(request)
    
    def to_manifest(self) -> Dict:
        """Generate manifest for deployment"""
        return {
            "name": self._name,
            "runtime": self.config.runtime,
            "regions": self.config.regions,
            "memory": self.config.memory,
            "timeout": self.config.timeout,
        }


class EdgeContext:
    """
    Edge request context with geo and performance info.
    """
    
    def __init__(self, request):
        self.request = request
        
    @property
    def geo(self) -> Dict:
        """Get geo information from headers"""
        return {
            "country": self._get_header("cf-ipcountry") or self._get_header("x-vercel-ip-country"),
            "city": self._get_header("cf-ipcity") or self._get_header("x-vercel-ip-city"),
            "region": self._get_header("cf-region") or self._get_header("x-vercel-ip-country-region"),
            "latitude": self._get_header("cf-iplatitude") or self._get_header("x-vercel-ip-latitude"),
            "longitude": self._get_header("cf-iplongitude") or self._get_header("x-vercel-ip-longitude"),
        }
    
    @property
    def is_bot(self) -> bool:
        """Detect if request is from a bot"""
        ua = self._get_header("user-agent", "").lower()
        bot_keywords = ["bot", "crawler", "spider", "scraper", "curl", "wget"]
        return any(kw in ua for kw in bot_keywords)
    
    def _get_header(self, name: str, default: str = None) -> Optional[str]:
        """Get header value"""
        headers = getattr(self.request, 'headers', {})
        return headers.get(name, default)


class EdgeCache:
    """
    Edge caching utilities.
    
    Usage:
        @edge
        @cache(ttl=3600)  # Cache for 1 hour
        def my_handler(request):
            return expensive_operation()
    """
    
    def __init__(self, ttl: int = 60, stale_while_revalidate: int = None):
        self.ttl = ttl
        self.swr = stale_while_revalidate
    
    def __call__(self, func):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            # Generate cache key
            cache_key = self._generate_key(request)
            
            # Add cache headers to response
            response = await func(request, *args, **kwargs) if asyncio.iscoroutinefunction(func) else func(request, *args, **kwargs)
            
            # If response is dict, wrap with headers
            if isinstance(response, dict):
                response = {
                    "data": response,
                    "_cache": {
                        "key": cache_key,
                        "ttl": self.ttl,
                        "headers": self._cache_headers()
                    }
                }
            
            return response
        return wrapper
    
    def _generate_key(self, request) -> str:
        """Generate cache key from request"""
        path = getattr(request, 'url', {})
        if hasattr(path, 'path'):
            path = path.path
        return f"edge:{path}"
    
    def _cache_headers(self) -> Dict[str, str]:
        """Generate cache control headers"""
        headers = {
            "Cache-Control": f"public, max-age={self.ttl}"
        }
        if self.swr:
            headers["Cache-Control"] += f", stale-while-revalidate={self.swr}"
        return headers


def edge(func=None, *, regions: List[str] = None, memory: int = 128, timeout: int = 30):
    """
    Decorator to mark a function as an edge function.
    
    Usage:
        @edge
        def handler(request):
            return {"hello": "world"}
        
        @edge(regions=["iad1"])
        def regional_handler(request):
            return {"region": "US East"}
    """
    def decorator(f):
        config = EdgeConfig(
            regions=regions or ["auto"],
            memory=memory,
            timeout=timeout,
        )
        return EdgeFunction(f, config)
    
    if func is not None:
        return decorator(func)
    return decorator


def cache(ttl: int = 60, stale_while_revalidate: int = None):
    """
    Decorator for edge caching.
    
    Usage:
        @edge
        @cache(ttl=3600)
        def cached_handler(request):
            return expensive_data()
    """
    return EdgeCache(ttl, stale_while_revalidate)


class EdgeDeployer:
    """
    Deploy PyX app to edge platforms.
    
    Supports:
    - Vercel Edge Functions
    - Cloudflare Workers
    - Deno Deploy
    """
    
    def __init__(self, platform: str = "vercel"):
        self.platform = platform
        self._functions: List[EdgeFunction] = []
    
    def register(self, func: EdgeFunction):
        """Register an edge function"""
        self._functions.append(func)
    
    def generate_config(self, output_dir: str = "dist"):
        """Generate deployment configuration"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if self.platform == "vercel":
            self._generate_vercel_config(output_path)
        elif self.platform == "cloudflare":
            self._generate_cloudflare_config(output_path)
        elif self.platform == "deno":
            self._generate_deno_config(output_path)
    
    def _generate_vercel_config(self, output_path: Path):
        """Generate Vercel configuration"""
        config = {
            "version": 3,
            "functions": {},
            "routes": []
        }
        
        for func in self._functions:
            manifest = func.to_manifest()
            config["functions"][f"api/{manifest['name']}.py"] = {
                "runtime": "python3.9",
                "memory": manifest["memory"],
                "maxDuration": manifest["timeout"],
            }
            config["routes"].append({
                "src": f"/api/{manifest['name']}",
                "dest": f"/api/{manifest['name']}.py"
            })
        
        with open(output_path / "vercel.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Generated vercel.json")
    
    def _generate_cloudflare_config(self, output_path: Path):
        """Generate Cloudflare Workers configuration"""
        config = {
            "name": "pyx-app",
            "main": "worker.py",
            "compatibility_date": "2024-01-01",
        }
        
        with open(output_path / "wrangler.toml", 'w') as f:
            for key, value in config.items():
                if isinstance(value, str):
                    f.write(f'{key} = "{value}"\n')
                else:
                    f.write(f'{key} = {value}\n')
        
        print(f"✅ Generated wrangler.toml")
    
    def _generate_deno_config(self, output_path: Path):
        """Generate Deno Deploy configuration"""
        config = {
            "tasks": {
                "start": "deno run --allow-net --allow-read main.ts"
            },
            "imports": {}
        }
        
        with open(output_path / "deno.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Generated deno.json")


class Middleware:
    """
    Edge middleware for request/response modification.
    
    Usage:
        @middleware
        def auth_middleware(request, next):
            if not is_authenticated(request):
                return redirect("/login")
            return next(request)
    """
    
    def __init__(self, handler: Callable):
        self.handler = handler
    
    async def __call__(self, request, next_handler: Callable):
        """Execute middleware"""
        if asyncio.iscoroutinefunction(self.handler):
            return await self.handler(request, next_handler)
        return self.handler(request, next_handler)


def middleware(func):
    """Decorator to create edge middleware"""
    return Middleware(func)


# Utility functions

def rewrite(destination: str) -> Dict:
    """Rewrite request to different path"""
    return {"type": "rewrite", "destination": destination}


def redirect(destination: str, permanent: bool = False) -> Dict:
    """Redirect to different URL"""
    return {
        "type": "redirect",
        "destination": destination,
        "permanent": permanent,
        "status": 308 if permanent else 307
    }


def next_response(body: Any = None, status: int = 200, headers: Dict = None) -> Dict:
    """Create a response"""
    return {
        "type": "response",
        "body": body,
        "status": status,
        "headers": headers or {}
    }
