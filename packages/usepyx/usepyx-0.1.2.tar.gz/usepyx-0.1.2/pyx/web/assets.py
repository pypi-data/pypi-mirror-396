import os
import hashlib
from PIL import Image
from io import BytesIO
import requests
from typing import Optional

class AssetManager:
    """
    PyX Asset Optimizer (The 'Next/Image' Killer).
    Handles on-the-fly image optimization and caching.
    """
    
    CACHE_DIR = ".pyx/cache/images"
    
    def __init__(self):
        os.makedirs(self.CACHE_DIR, exist_ok=True)
        
    def _get_cache_path(self, key: str) -> str:
        return os.path.join(self.CACHE_DIR, f"{key}.webp")
        
    def _generate_key(self, url: str, width: int, quality: int) -> str:
        """Generate unique cache key based on params"""
        raw = f"{url}-{width}-{quality}"
        return hashlib.md5(raw.encode()).hexdigest()

    def optimize(self, url: str, width: int = 800, quality: int = 80) -> Optional[bytes]:
        """
        Optimize image:
        1. Check cache.
        2. Download/Read image.
        3. Resize & Convert to WebP.
        4. Save to cache.
        5. Return bytes.
        """
        key = self._generate_key(url, width, quality)
        cache_path = self._get_cache_path(key)
        
        # 1. HIT CACHE
        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                return f.read()
                
        # 2. MISS CACHE - PROCESS
        try:
            img = None
            
            # Load from URL or Local
            if url.startswith("http"):
                response = requests.get(url, stream=True)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))
            else:
                # Local file
                # Remove leading slash if present to make it relative to cwd
                local_path = url.lstrip("/") 
                if not os.path.exists(local_path):
                    print(f"[PyX Image] File not found: {local_path}")
                    return None
                img = Image.open(local_path)
            
            # 3. OPTIMIZE
            # Convert to RGB (remove alpha only if saving as JPEG, but we use WebP which supports Alpha)
            # Actually WebP supports RGBA, so we are good.
            
            # Resize (Maintain Aspect Ratio)
            w_percent = (width / float(img.size[0]))
            h_size = int((float(img.size[1]) * float(w_percent)))
            img = img.resize((width, h_size), Image.Resampling.LANCZOS)
            
            # Save to buffer
            buf = BytesIO()
            img.save(buf, "WEBP", quality=quality)
            data = buf.getvalue()
            
            # 4. SAVE CACHE
            with open(cache_path, "wb") as f:
                f.write(data)
                
            return data
            
        except Exception as e:
            print(f"[PyX Image] Optimization failed for {url}: {e}")
            return None

assets = AssetManager()
