"""
PyX Static Site Generation (SSG)
Generate static HTML files for deployment.
"""
import os
import json
import shutil
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BuildConfig:
    """Build configuration"""
    output_dir: str = "dist"
    pages_dir: str = "pages"
    public_dir: str = "public"
    assets_dir: str = "assets"
    minify: bool = True
    generate_sitemap: bool = True
    base_url: str = "/"
    
    # SSG specific
    static_paths: List[str] = None  # Paths to pre-render
    dynamic_paths: Dict[str, Callable] = None  # Function to generate dynamic paths
    
    def __post_init__(self):
        if self.static_paths is None:
            self.static_paths = []
        if self.dynamic_paths is None:
            self.dynamic_paths = {}


class StaticSiteGenerator:
    """
    SSG Builder for PyX.
    
    Usage:
        ssg = StaticSiteGenerator()
        ssg.build()
        
    CLI:
        pyx build        # Build static site
        pyx export       # Same as build
        
    Output:
        dist/
        ├── index.html
        ├── about.html
        ├── blog/
        │   ├── index.html
        │   ├── my-first-post.html
        │   └── another-post.html
        ├── assets/
        │   ├── style.css
        │   └── app.js
        └── sitemap.xml
    """
    
    def __init__(self, config: BuildConfig = None):
        self.config = config or BuildConfig()
        self.output_dir = Path(self.config.output_dir)
        self.pages_dir = Path(self.config.pages_dir)
        self.public_dir = Path(self.config.public_dir)
        self._built_pages: List[Dict] = []
    
    def build(self) -> bool:
        """Build the static site"""
        print("\n🔨 PyX Static Site Generator\n")
        print(f"   Output: {self.output_dir}")
        print(f"   Pages:  {self.pages_dir}")
        print()
        
        start_time = datetime.now()
        
        # Clean output directory
        self._clean_output()
        
        # Copy public assets
        self._copy_public()
        
        # Discover and build pages
        self._build_pages()
        
        # Generate sitemap
        if self.config.generate_sitemap:
            self._generate_sitemap()
        
        # Generate manifest
        self._generate_manifest()
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print(f"\n✅ Build complete in {elapsed:.2f}s")
        print(f"   Generated {len(self._built_pages)} pages")
        print(f"   Output: {self.output_dir.absolute()}")
        
        return True
    
    def _clean_output(self):
        """Clean output directory"""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True)
        print("   📁 Cleaned output directory")
    
    def _copy_public(self):
        """Copy public assets"""
        if self.public_dir.exists():
            shutil.copytree(self.public_dir, self.output_dir, dirs_exist_ok=True)
            print(f"   📦 Copied public assets")
        
        # Also copy assets dir if exists
        assets_dir = Path(self.config.assets_dir)
        if assets_dir.exists():
            dest = self.output_dir / "assets"
            shutil.copytree(assets_dir, dest, dirs_exist_ok=True)
            print(f"   📦 Copied assets")
    
    def _build_pages(self):
        """Build all pages"""
        from .file_router import FileRouter
        
        print("\n   📄 Building pages:")
        
        router = FileRouter(str(self.pages_dir))
        routes = router.discover()
        
        for path, route in routes.items():
            if route.is_api:
                continue  # Skip API routes
            
            if route.is_dynamic:
                # Handle dynamic routes
                self._build_dynamic_page(route)
            else:
                # Static page
                self._build_static_page(route)
    
    def _build_static_page(self, route):
        """Build a static page"""
        try:
            # Call the handler to get content
            content = route.handler()
            html = self._render_to_html(content, route.path)
            
            # Determine output path
            output_path = self._get_output_path(route.path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write HTML
            with open(output_path, 'w') as f:
                f.write(html)
            
            self._built_pages.append({
                "path": route.path,
                "file": str(output_path.relative_to(self.output_dir)),
            })
            
            print(f"      ✓ {route.path} → {output_path.name}")
            
        except Exception as e:
            print(f"      ✗ {route.path} - Error: {e}")
    
    def _build_dynamic_page(self, route):
        """Build pages for dynamic route"""
        param_name = route.dynamic_params[0] if route.dynamic_params else "id"
        
        # Check if we have path generator
        if route.path in self.config.dynamic_paths:
            paths = self.config.dynamic_paths[route.path]()
        else:
            # Try to get getStaticPaths from module
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("page", route.file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'get_static_paths'):
                    paths = module.get_static_paths()
                else:
                    print(f"      ⚠ {route.path} - No get_static_paths(), skipping")
                    return
            except:
                return
        
        # Build each path
        for params in paths:
            try:
                # Replace dynamic segments
                actual_path = route.path
                for key, value in params.items():
                    actual_path = actual_path.replace(f":{key}", str(value))
                
                # Call handler with params
                content = route.handler(**params)
                html = self._render_to_html(content, actual_path)
                
                output_path = self._get_output_path(actual_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'w') as f:
                    f.write(html)
                
                self._built_pages.append({
                    "path": actual_path,
                    "file": str(output_path.relative_to(self.output_dir)),
                })
                
                print(f"      ✓ {actual_path}")
                
            except Exception as e:
                print(f"      ✗ {actual_path} - Error: {e}")
    
    def _get_output_path(self, route_path: str) -> Path:
        """Convert route path to output file path"""
        if route_path == "/":
            return self.output_dir / "index.html"
        
        # Remove leading slash
        clean_path = route_path.lstrip("/")
        
        # Check if already has extension
        if clean_path.endswith(".html"):
            return self.output_dir / clean_path
        
        # Convert to directory/index.html or file.html
        if "/" in clean_path:
            return self.output_dir / clean_path / "index.html"
        else:
            return self.output_dir / f"{clean_path}.html"
    
    def _render_to_html(self, content, path: str) -> str:
        """Render content to full HTML document"""
        if hasattr(content, 'render'):
            body = content.render()
        else:
            body = str(content)
        
        # Get page title
        title = path.replace("/", " ").strip().title() or "Home"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | PyX</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
    </style>
</head>
<body>
    <div id="app">{body}</div>
    <script>
        lucide.createIcons();
    </script>
</body>
</html>"""
        
        if self.config.minify:
            html = self._minify_html(html)
        
        return html
    
    def _minify_html(self, html: str) -> str:
        """Basic HTML minification"""
        import re
        # Remove extra whitespace
        html = re.sub(r'\s+', ' ', html)
        html = re.sub(r'>\s+<', '><', html)
        return html.strip()
    
    def _generate_sitemap(self):
        """Generate sitemap.xml"""
        base_url = self.config.base_url.rstrip("/")
        
        urls = []
        for page in self._built_pages:
            urls.append(f"""  <url>
    <loc>{base_url}{page['path']}</loc>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
  </url>""")
        
        sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""
        
        with open(self.output_dir / "sitemap.xml", 'w') as f:
            f.write(sitemap)
        
        print("\n   🗺️  Generated sitemap.xml")
    
    def _generate_manifest(self):
        """Generate build manifest"""
        manifest = {
            "pages": self._built_pages,
            "buildTime": datetime.now().isoformat(),
            "config": {
                "minify": self.config.minify,
                "baseUrl": self.config.base_url,
            }
        }
        
        with open(self.output_dir / ".manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)


class IncrementalBuilder:
    """
    Incremental Static Regeneration (ISR).
    Rebuild only changed pages.
    """
    
    def __init__(self, config: BuildConfig = None):
        self.config = config or BuildConfig()
        self.output_dir = Path(self.config.output_dir)
        self._cache_file = self.output_dir / ".build_cache.json"
        self._file_hashes: Dict[str, str] = {}
    
    def _get_file_hash(self, path: Path) -> str:
        """Get hash of file contents"""
        import hashlib
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _load_cache(self):
        """Load build cache"""
        if self._cache_file.exists():
            with open(self._cache_file) as f:
                self._file_hashes = json.load(f)
    
    def _save_cache(self):
        """Save build cache"""
        self._cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._cache_file, 'w') as f:
            json.dump(self._file_hashes, f, indent=2)
    
    def get_changed_files(self, pages_dir: str = "pages") -> List[Path]:
        """Get list of changed files since last build"""
        self._load_cache()
        
        changed = []
        pages_path = Path(pages_dir)
        
        for py_file in pages_path.rglob("*.py"):
            current_hash = self._get_file_hash(py_file)
            cached_hash = self._file_hashes.get(str(py_file))
            
            if cached_hash != current_hash:
                changed.append(py_file)
                self._file_hashes[str(py_file)] = current_hash
        
        self._save_cache()
        return changed
    
    def build_incremental(self):
        """Build only changed pages"""
        changed = self.get_changed_files()
        
        if not changed:
            print("ℹ️  No changes detected, skipping build")
            return
        
        print(f"🔄 Rebuilding {len(changed)} changed pages:")
        for f in changed:
            print(f"   • {f}")
        
        # TODO: Only rebuild changed pages
        ssg = StaticSiteGenerator(self.config)
        ssg.build()
