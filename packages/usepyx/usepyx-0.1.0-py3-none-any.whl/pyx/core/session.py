"""
PyX Session Persistence Layer
Enables state to persist across page refreshes using cookies/localStorage.

This module provides:
- Session ID generation and management
- Cookie-based session tracking
- Optional localStorage sync for client-side persistence
"""

from typing import Any, Dict, Optional, Type
import uuid
import json
import hashlib
from datetime import datetime, timedelta


class SessionConfig:
    """Session configuration."""
    
    # How long sessions last (in seconds)
    SESSION_LIFETIME: int = 3600 * 24  # 24 hours
    
    # Cookie settings
    COOKIE_NAME: str = "pyx_session"
    COOKIE_HTTPONLY: bool = True
    COOKIE_SECURE: bool = False  # Set True in production with HTTPS
    COOKIE_SAMESITE: str = "lax"
    
    # Storage backend (memory, redis, file)
    STORAGE_BACKEND: str = "memory"


class SessionStorage:
    """
    In-memory session storage.
    For production, extend with Redis/Database backend.
    """
    
    _sessions: Dict[str, Dict[str, Any]] = {}
    _expiry: Dict[str, datetime] = {}
    
    @classmethod
    def get(cls, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data."""
        if session_id in cls._sessions:
            # Check expiry
            if session_id in cls._expiry:
                if datetime.now() > cls._expiry[session_id]:
                    cls.delete(session_id)
                    return None
            return cls._sessions.get(session_id)
        return None
    
    @classmethod
    def set(cls, session_id: str, data: Dict[str, Any], lifetime: int = None):
        """Set session data."""
        cls._sessions[session_id] = data
        if lifetime:
            cls._expiry[session_id] = datetime.now() + timedelta(seconds=lifetime)
    
    @classmethod
    def update(cls, session_id: str, key: str, value: Any):
        """Update a specific key in session."""
        if session_id not in cls._sessions:
            cls._sessions[session_id] = {}
        cls._sessions[session_id][key] = value
    
    @classmethod
    def delete(cls, session_id: str):
        """Delete session."""
        if session_id in cls._sessions:
            del cls._sessions[session_id]
        if session_id in cls._expiry:
            del cls._expiry[session_id]
    
    @classmethod
    def cleanup(cls):
        """Remove expired sessions."""
        now = datetime.now()
        expired = [sid for sid, exp in cls._expiry.items() if now > exp]
        for sid in expired:
            cls.delete(sid)


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return hashlib.sha256(
        f"{uuid.uuid4()}{datetime.now().isoformat()}".encode()
    ).hexdigest()[:32]


class Session:
    """
    Session object for request/response cycle.
    
    Usage in a route handler:
        def my_handler(request):
            session = Session.from_request(request)
            session['user_id'] = 123
            response = make_response()
            session.save(response)
            return response
    """
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or generate_session_id()
        self._data = SessionStorage.get(self.session_id) or {}
        self._modified = False
    
    def __getitem__(self, key: str) -> Any:
        return self._data.get(key)
    
    def __setitem__(self, key: str, value: Any):
        self._data[key] = value
        self._modified = True
    
    def __delitem__(self, key: str):
        if key in self._data:
            del self._data[key]
            self._modified = True
    
    def __contains__(self, key: str) -> bool:
        return key in self._data
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)
    
    def set(self, key: str, value: Any):
        self[key] = value
    
    def clear(self):
        """Clear all session data."""
        self._data = {}
        self._modified = True
    
    def save(self):
        """Save session to storage."""
        SessionStorage.set(
            self.session_id, 
            self._data, 
            SessionConfig.SESSION_LIFETIME
        )
    
    @classmethod
    def from_cookie(cls, cookie_value: str) -> 'Session':
        """Create session from cookie value."""
        if cookie_value:
            return cls(session_id=cookie_value)
        return cls()
    
    def get_cookie_header(self) -> str:
        """Generate Set-Cookie header value."""
        parts = [
            f"{SessionConfig.COOKIE_NAME}={self.session_id}",
            f"Max-Age={SessionConfig.SESSION_LIFETIME}",
            "Path=/",
            f"SameSite={SessionConfig.COOKIE_SAMESITE}",
        ]
        if SessionConfig.COOKIE_HTTPONLY:
            parts.append("HttpOnly")
        if SessionConfig.COOKIE_SECURE:
            parts.append("Secure")
        return "; ".join(parts)


# Client-side persistence helper (JavaScript)
def get_client_storage_js() -> str:
    """
    Returns JavaScript code for client-side state persistence.
    Syncs state to localStorage for faster hydration on reload.
    """
    return """
    <script>
    window.PyXPersistence = {
        // Save state to localStorage
        save: function(key, value) {
            try {
                localStorage.setItem('pyx_state_' + key, JSON.stringify(value));
            } catch(e) {
                console.warn('PyX: Failed to save to localStorage', e);
            }
        },
        
        // Load state from localStorage
        load: function(key) {
            try {
                const data = localStorage.getItem('pyx_state_' + key);
                return data ? JSON.parse(data) : null;
            } catch(e) {
                console.warn('PyX: Failed to load from localStorage', e);
                return null;
            }
        },
        
        // Clear persisted state
        clear: function(key) {
            if (key) {
                localStorage.removeItem('pyx_state_' + key);
            } else {
                // Clear all PyX state
                Object.keys(localStorage).forEach(k => {
                    if (k.startsWith('pyx_state_')) {
                        localStorage.removeItem(k);
                    }
                });
            }
        },
        
        // Sync state vars on page load
        hydrate: function(stateVars) {
            Object.keys(stateVars).forEach(key => {
                const saved = this.load(key);
                if (saved !== null) {
                    stateVars[key] = saved;
                }
            });
            return stateVars;
        }
    };
    </script>
    """


# Export
__all__ = [
    'Session',
    'SessionStorage',
    'SessionConfig',
    'generate_session_id',
    'get_client_storage_js',
]
