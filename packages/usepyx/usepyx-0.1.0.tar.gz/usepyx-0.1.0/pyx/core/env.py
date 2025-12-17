"""
PyX Environment Configuration
Load configuration from .env file.
"""
import os
from typing import Any, Optional


class Env:
    """
    Environment configuration loader.
    
    Usage:
        from pyx import env
        
        # Load .env file (auto-loaded on import)
        env.load()
        
        # Get values
        db_url = env.get("DATABASE_URL")
        debug = env.bool("DEBUG", default=False)
        port = env.int("PORT", default=8000)
        
        # Required value (raises error if missing)
        secret = env.require("SECRET_KEY")
    """
    
    _loaded = False
    _values = {}
    
    @classmethod
    def load(cls, path: str = ".env"):
        """
        Load environment variables from .env file.
        
        Args:
            path: Path to .env file (default: .env)
        """
        if not os.path.exists(path):
            return
        
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                
                # Parse KEY=VALUE
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    # Store in both places
                    cls._values[key] = value
                    os.environ[key] = value
        
        cls._loaded = True
        print(f"[PyX Env] Loaded {len(cls._values)} variables from {path}")
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Optional[str]:
        """
        Get environment variable.
        
        Args:
            key: Variable name
            default: Default value if not found
        """
        return os.environ.get(key, cls._values.get(key, default))
    
    @classmethod
    def require(cls, key: str) -> str:
        """
        Get required environment variable.
        Raises error if not found.
        """
        value = cls.get(key)
        if value is None:
            raise EnvironmentError(f"Required environment variable '{key}' is not set")
        return value
    
    @classmethod
    def bool(cls, key: str, default: bool = False) -> bool:
        """Get environment variable as boolean"""
        value = cls.get(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")
    
    @classmethod
    def int(cls, key: str, default: int = 0) -> int:
        """Get environment variable as integer"""
        value = cls.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default
    
    @classmethod
    def float(cls, key: str, default: float = 0.0) -> float:
        """Get environment variable as float"""
        value = cls.get(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default
    
    @classmethod
    def list(cls, key: str, separator: str = ",", default: list = None) -> list:
        """Get environment variable as list"""
        value = cls.get(key)
        if value is None:
            return default or []
        return [v.strip() for v in value.split(separator)]
    
    @classmethod
    def all(cls) -> dict:
        """Get all loaded environment variables"""
        return cls._values.copy()
    
    @classmethod
    def set(cls, key: str, value: Any):
        """Set environment variable"""
        str_value = str(value)
        cls._values[key] = str_value
        os.environ[key] = str_value
    
    @classmethod
    def has(cls, key: str) -> bool:
        """Check if environment variable exists"""
        return key in os.environ or key in cls._values


# Global instance
env = Env()

# Auto-load .env on import
if os.path.exists(".env"):
    env.load()
