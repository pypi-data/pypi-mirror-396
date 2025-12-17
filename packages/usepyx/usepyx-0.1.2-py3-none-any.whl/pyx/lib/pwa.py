"""
PyX Progressive Web App (PWA) Support
Make PyX apps installable with offline support.
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class PWAIcon:
    """PWA Icon configuration"""
    src: str
    sizes: str  # "192x192", "512x512"
    type: str = "image/png"
    purpose: str = "any maskable"


@dataclass
class PWAConfig:
    """
    PWA Manifest configuration.
    
    Usage:
        config = PWAConfig(
            name="My App",
            short_name="App",
            theme_color="#3B82F6",
            icons=[
                PWAIcon("/icons/icon-192.png", "192x192"),
                PWAIcon("/icons/icon-512.png", "512x512"),
            ]
        )
    """
    name: str
    short_name: str = None
    description: str = ""
    theme_color: str = "#3B82F6"
    background_color: str = "#ffffff"
    display: str = "standalone"  # "fullscreen", "standalone", "minimal-ui", "browser"
    orientation: str = "any"  # "any", "portrait", "landscape"
    start_url: str = "/"
    scope: str = "/"
    icons: List[PWAIcon] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    screenshots: List[Dict] = field(default_factory=list)
    shortcuts: List[Dict] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.short_name:
            self.short_name = self.name[:12]
        
        # Default icons if none provided
        if not self.icons:
            self.icons = [
                PWAIcon("/icon-192.png", "192x192"),
                PWAIcon("/icon-512.png", "512x512"),
            ]
    
    def to_manifest(self) -> Dict:
        """Generate manifest.json content"""
        manifest = {
            "name": self.name,
            "short_name": self.short_name,
            "description": self.description,
            "theme_color": self.theme_color,
            "background_color": self.background_color,
            "display": self.display,
            "orientation": self.orientation,
            "start_url": self.start_url,
            "scope": self.scope,
            "icons": [
                {
                    "src": icon.src,
                    "sizes": icon.sizes,
                    "type": icon.type,
                    "purpose": icon.purpose
                }
                for icon in self.icons
            ]
        }
        
        if self.categories:
            manifest["categories"] = self.categories
        if self.screenshots:
            manifest["screenshots"] = self.screenshots
        if self.shortcuts:
            manifest["shortcuts"] = self.shortcuts
        
        return manifest


class PWA:
    """
    PWA Manager for PyX apps.
    
    Usage:
        from pyx import PWA, PWAConfig
        
        pwa = PWA(PWAConfig(
            name="My PWA App",
            theme_color="#3B82F6"
        ))
        
        # Generate files
        pwa.generate()
        
        # Get head tags
        pwa.head_tags()
    """
    
    def __init__(self, config: PWAConfig):
        self.config = config
    
    def generate(self, output_dir: str = "public"):
        """Generate PWA files (manifest.json, service-worker.js)"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate manifest.json
        manifest_path = output_path / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(self.config.to_manifest(), f, indent=2)
        print(f"✅ Generated {manifest_path}")
        
        # Generate service worker
        sw_path = output_path / "sw.js"
        with open(sw_path, 'w') as f:
            f.write(self._generate_service_worker())
        print(f"✅ Generated {sw_path}")
        
        # Generate offline page
        offline_path = output_path / "offline.html"
        with open(offline_path, 'w') as f:
            f.write(self._generate_offline_page())
        print(f"✅ Generated {offline_path}")
    
    def _generate_service_worker(self) -> str:
        """Generate service worker JavaScript"""
        return f'''// PyX Service Worker
const CACHE_NAME = 'pyx-cache-v1';
const OFFLINE_URL = '/offline.html';

// Files to cache
const STATIC_ASSETS = [
    '/',
    '/offline.html',
    '/manifest.json',
    'https://cdn.tailwindcss.com',
    'https://unpkg.com/lucide@latest'
];

// Install event
self.addEventListener('install', (event) => {{
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {{
            console.log('[SW] Caching static assets');
            return cache.addAll(STATIC_ASSETS);
        }})
    );
    self.skipWaiting();
}});

// Activate event
self.addEventListener('activate', (event) => {{
    event.waitUntil(
        caches.keys().then((cacheNames) => {{
            return Promise.all(
                cacheNames.map((cacheName) => {{
                    if (cacheName !== CACHE_NAME) {{
                        console.log('[SW] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }}
                }})
            );
        }})
    );
    self.clients.claim();
}});

// Fetch event - Network first, fallback to cache
self.addEventListener('fetch', (event) => {{
    // Skip non-GET requests
    if (event.request.method !== 'GET') return;
    
    // Skip WebSocket requests
    if (event.request.url.includes('/ws')) return;
    
    event.respondWith(
        fetch(event.request)
            .then((response) => {{
                // Clone and cache successful responses
                if (response.ok) {{
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => {{
                        cache.put(event.request, responseClone);
                    }});
                }}
                return response;
            }})
            .catch(() => {{
                // Network failed, try cache
                return caches.match(event.request).then((cachedResponse) => {{
                    if (cachedResponse) {{
                        return cachedResponse;
                    }}
                    // If it's a navigation request, show offline page
                    if (event.request.mode === 'navigate') {{
                        return caches.match(OFFLINE_URL);
                    }}
                    return new Response('Offline', {{ status: 503 }});
                }});
            }})
    );
}});

// Push notification event
self.addEventListener('push', (event) => {{
    const data = event.data ? event.data.json() : {{}};
    const title = data.title || '{self.config.name}';
    const options = {{
        body: data.body || 'New notification',
        icon: '/icon-192.png',
        badge: '/icon-192.png',
        data: data.url || '/'
    }};
    
    event.waitUntil(
        self.registration.showNotification(title, options)
    );
}});

// Notification click event
self.addEventListener('notificationclick', (event) => {{
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data)
    );
}});
'''
    
    def _generate_offline_page(self) -> str:
        """Generate offline fallback page"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Offline - {self.config.name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen flex items-center justify-center p-4">
    <div class="text-center">
        <div class="mb-6">
            <svg class="w-24 h-24 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
                      d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3"/>
            </svg>
        </div>
        <h1 class="text-2xl font-bold text-gray-800 mb-2">You're Offline</h1>
        <p class="text-gray-600 mb-6">Please check your internet connection and try again.</p>
        <button onclick="location.reload()" 
                class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            Try Again
        </button>
    </div>
</body>
</html>
'''
    
    def head_tags(self) -> str:
        """
        Generate head tags for PWA.
        Include this in your HTML head.
        """
        return f'''
<!-- PWA Meta Tags -->
<meta name="application-name" content="{self.config.short_name}">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="{self.config.short_name}">
<meta name="mobile-web-app-capable" content="yes">
<meta name="theme-color" content="{self.config.theme_color}">

<!-- PWA Manifest -->
<link rel="manifest" href="/manifest.json">

<!-- Apple Touch Icon -->
<link rel="apple-touch-icon" href="/icon-192.png">

<!-- PWA Service Worker Registration -->
<script>
    if ('serviceWorker' in navigator) {{
        window.addEventListener('load', () => {{
            navigator.serviceWorker.register('/sw.js')
                .then((registration) => {{
                    console.log('SW registered:', registration.scope);
                }})
                .catch((error) => {{
                    console.log('SW registration failed:', error);
                }});
        }});
    }}
</script>
'''
    
    def install_prompt(self, button_text: str = "Install App") -> str:
        """
        Generate install prompt component.
        Shows a button to install the PWA.
        """
        return f'''
<div id="pwa-install-prompt" class="hidden fixed bottom-4 right-4 p-4 bg-white rounded-lg shadow-lg border z-50">
    <div class="flex items-center gap-4">
        <div class="flex-1">
            <p class="font-medium text-gray-800">Install {self.config.name}</p>
            <p class="text-sm text-gray-500">Add to your home screen</p>
        </div>
        <button id="pwa-install-btn" 
                class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            {button_text}
        </button>
        <button id="pwa-dismiss-btn" class="p-2 text-gray-400 hover:text-gray-600">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
        </button>
    </div>
</div>

<script>
    let deferredPrompt;
    const promptEl = document.getElementById('pwa-install-prompt');
    const installBtn = document.getElementById('pwa-install-btn');
    const dismissBtn = document.getElementById('pwa-dismiss-btn');
    
    window.addEventListener('beforeinstallprompt', (e) => {{
        e.preventDefault();
        deferredPrompt = e;
        promptEl.classList.remove('hidden');
    }});
    
    installBtn?.addEventListener('click', async () => {{
        if (deferredPrompt) {{
            deferredPrompt.prompt();
            const {{ outcome }} = await deferredPrompt.userChoice;
            console.log('Install outcome:', outcome);
            deferredPrompt = null;
            promptEl.classList.add('hidden');
        }}
    }});
    
    dismissBtn?.addEventListener('click', () => {{
        promptEl.classList.add('hidden');
    }});
    
    window.addEventListener('appinstalled', () => {{
        console.log('PWA installed');
        promptEl.classList.add('hidden');
    }});
</script>
'''


def pwa_head(config: PWAConfig) -> str:
    """
    Quick helper to generate PWA head tags.
    
    Usage:
        pwa_head(PWAConfig(name="My App"))
    """
    return PWA(config).head_tags()
