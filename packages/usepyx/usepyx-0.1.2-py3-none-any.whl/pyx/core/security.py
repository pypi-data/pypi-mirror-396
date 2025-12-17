"""
PyX Security Module
Centralized security utilities with Zen Mode access.
"""
import secrets
import hashlib
import hmac
import base64
import re
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from functools import wraps


# =============================================================================
# PASSWORD HASHING (Bcrypt with fallback)
# =============================================================================

class PasswordHasher:
    """
    Secure password hashing using bcrypt (recommended) with SHA256 fallback.
    
    Usage:
        from pyx import security
        
        # Hash password
        hash = security.hash_password("my_password")
        
        # Verify
        if security.verify_password("my_password", hash):
            print("Valid!")
    """
    
    _use_bcrypt = True
    
    @classmethod
    def _try_bcrypt(cls):
        """Check if bcrypt is available"""
        try:
            import bcrypt
            return bcrypt
        except ImportError:
            cls._use_bcrypt = False
            return None
    
    @classmethod
    def hash(cls, password: str, rounds: int = 12) -> str:
        """
        Hash password securely.
        
        Uses bcrypt if available, falls back to SHA256+salt.
        """
        bcrypt = cls._try_bcrypt()
        
        if bcrypt:
            # Bcrypt (recommended)
            salt = bcrypt.gensalt(rounds=rounds)
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        else:
            # Fallback: SHA256 with salt (not recommended for production)
            import warnings
            warnings.warn(
                "bcrypt not installed! Using SHA256 fallback. "
                "Install bcrypt for better security: pip install bcrypt",
                SecurityWarning
            )
            salt = secrets.token_hex(32)
            # Use PBKDF2 for key derivation
            key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                iterations=100000
            )
            return f"pbkdf2:sha256:100000${salt}${key.hex()}"
    
    @classmethod
    def verify(cls, password: str, password_hash: str) -> bool:
        """
        Verify password against hash.
        
        Automatically detects hash format (bcrypt or pbkdf2).
        """
        if not password or not password_hash:
            return False
        
        try:
            # Check if bcrypt hash (starts with $2)
            if password_hash.startswith('$2'):
                bcrypt = cls._try_bcrypt()
                if bcrypt:
                    return bcrypt.checkpw(
                        password.encode('utf-8'),
                        password_hash.encode('utf-8')
                    )
                return False
            
            # PBKDF2 format: pbkdf2:sha256:iterations$salt$hash
            elif password_hash.startswith('pbkdf2:'):
                parts = password_hash.split('$')
                if len(parts) != 3:
                    return False
                
                header, salt, stored_hash = parts
                _, algorithm, iterations = header.split(':')
                
                key = hashlib.pbkdf2_hmac(
                    algorithm,
                    password.encode('utf-8'),
                    salt.encode('utf-8'),
                    iterations=int(iterations)
                )
                return hmac.compare_digest(key.hex(), stored_hash)
            
            # Legacy SHA256 format: salt$hash (for backward compatibility)
            elif '$' in password_hash and not password_hash.startswith('pbkdf2'):
                salt, stored_hash = password_hash.split('$', 1)
                hash_obj = hashlib.sha256((password + salt).encode())
                return hmac.compare_digest(hash_obj.hexdigest(), stored_hash)
            
            return False
            
        except Exception:
            return False


# =============================================================================
# SECURITY HEADERS
# =============================================================================

class SecurityHeaders:
    """
    Security headers for HTTP responses.
    
    Usage:
        app.use(security.headers())
    """
    
    DEFAULT_HEADERS = {
        # Prevent MIME sniffing
        "X-Content-Type-Options": "nosniff",
        
        # Clickjacking protection
        "X-Frame-Options": "DENY",
        
        # XSS Protection (legacy browsers)
        "X-XSS-Protection": "1; mode=block",
        
        # Referrer Policy
        "Referrer-Policy": "strict-origin-when-cross-origin",
        
        # Permissions Policy (formerly Feature-Policy)
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    }
    
    def __init__(
        self,
        hsts: bool = False,
        hsts_max_age: int = 31536000,
        csp: str = None,
        custom_headers: Dict[str, str] = None
    ):
        self.headers = self.DEFAULT_HEADERS.copy()
        
        # HSTS (only enable if using HTTPS)
        if hsts:
            self.headers["Strict-Transport-Security"] = f"max-age={hsts_max_age}; includeSubDomains"
        
        # Content Security Policy
        if csp:
            self.headers["Content-Security-Policy"] = csp
        else:
            # Default restrictive CSP
            self.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' ws: wss:;"
            )
        
        # Custom headers
        if custom_headers:
            self.headers.update(custom_headers)
    
    def __call__(self, request, call_next):
        """Middleware handler"""
        response = call_next(request)
        
        # Add security headers
        for header, value in self.headers.items():
            response.headers[header] = value
        
        return response


# =============================================================================
# PASSWORD POLICY
# =============================================================================

class PasswordPolicy:
    """
    Password strength validation.
    
    Usage:
        from pyx import security
        
        # Check password strength
        is_valid, errors = security.check_password("weak")
        # is_valid = False, errors = ["Password must be at least 8 characters"]
        
        # Strong password
        is_valid, errors = security.check_password("MyStr0ng!Pass")
        # is_valid = True, errors = []
    """
    
    def __init__(
        self,
        min_length: int = 8,
        max_length: int = 128,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digit: bool = True,
        require_special: bool = False,
        special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special
        self.special_chars = special_chars
    
    def validate(self, password: str) -> tuple:
        """
        Validate password against policy.
        
        Returns:
            (is_valid: bool, errors: List[str])
        """
        errors = []
        
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters")
        
        if len(password) > self.max_length:
            errors.append(f"Password must be at most {self.max_length} characters")
        
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.require_digit and not re.search(r'[0-9]', password):
            errors.append("Password must contain at least one digit")
        
        if self.require_special:
            pattern = f'[{re.escape(self.special_chars)}]'
            if not re.search(pattern, password):
                errors.append(f"Password must contain at least one special character ({self.special_chars})")
        
        return (len(errors) == 0, errors)
    
    def strength(self, password: str) -> dict:
        """
        Calculate password strength score.
        
        Returns:
            {
                "score": 0-100,
                "level": "weak" | "fair" | "good" | "strong",
                "suggestions": [...]
            }
        """
        score = 0
        suggestions = []
        
        # Length score (max 30 points)
        length = len(password)
        if length >= 16:
            score += 30
        elif length >= 12:
            score += 25
        elif length >= 8:
            score += 15
        else:
            score += length * 2
            suggestions.append("Use at least 8 characters")
        
        # Uppercase (10 points)
        if re.search(r'[A-Z]', password):
            score += 10
        else:
            suggestions.append("Add uppercase letters")
        
        # Lowercase (10 points)
        if re.search(r'[a-z]', password):
            score += 10
        else:
            suggestions.append("Add lowercase letters")
        
        # Digits (15 points)
        if re.search(r'[0-9]', password):
            score += 15
        else:
            suggestions.append("Add numbers")
        
        # Special chars (20 points)
        if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            score += 20
        else:
            suggestions.append("Add special characters")
        
        # Mixed case bonus (5 points)
        if re.search(r'[A-Z]', password) and re.search(r'[a-z]', password):
            score += 5
        
        # Variety bonus (10 points)
        char_types = sum([
            bool(re.search(r'[A-Z]', password)),
            bool(re.search(r'[a-z]', password)),
            bool(re.search(r'[0-9]', password)),
            bool(re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password)),
        ])
        if char_types >= 3:
            score += 10
        
        # Determine level
        if score >= 80:
            level = "strong"
        elif score >= 60:
            level = "good"
        elif score >= 40:
            level = "fair"
        else:
            level = "weak"
        
        return {
            "score": min(score, 100),
            "level": level,
            "suggestions": suggestions
        }


# =============================================================================
# HTTPS REDIRECT
# =============================================================================

class HTTPSRedirect:
    """
    Redirect HTTP to HTTPS middleware.
    
    Usage:
        app.use(security.https_redirect())
    """
    
    def __init__(self, exclude_paths: List[str] = None):
        self.exclude_paths = exclude_paths or ["/health", "/ping"]
    
    def __call__(self, request, call_next):
        # Skip in development
        host = request.headers.get("host", "")
        if "localhost" in host or "127.0.0.1" in host:
            return call_next(request)
        
        # Skip excluded paths
        for path in self.exclude_paths:
            if request.url.path.startswith(path):
                return call_next(request)
        
        # Check if HTTPS
        scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
        if scheme != "https":
            from starlette.responses import RedirectResponse
            https_url = request.url.replace(scheme="https")
            return RedirectResponse(str(https_url), status_code=301)
        
        return call_next(request)


# =============================================================================
# ACCOUNT LOCKOUT
# =============================================================================

class AccountLockout:
    """
    Prevent brute force attacks by locking accounts after failed attempts.
    
    Usage:
        from pyx import security
        
        # Check before login
        if security.lockout.is_locked(email):
            return "Account locked"
        
        # Record failed attempt
        security.lockout.record_failure(email)
        
        # Clear on success
        security.lockout.clear(email)
    """
    
    def __init__(
        self,
        max_attempts: int = 5,
        lockout_minutes: int = 15
    ):
        self.max_attempts = max_attempts
        self.lockout_minutes = lockout_minutes
        self._attempts: Dict[str, list] = {}  # identifier -> [timestamps]
        self._locked: Dict[str, datetime] = {}  # identifier -> locked_until
    
    def record_failure(self, identifier: str) -> bool:
        """
        Record a failed login attempt.
        
        Returns:
            True if account is now locked
        """
        now = datetime.now()
        
        # Clean old attempts
        if identifier in self._attempts:
            window_start = now - timedelta(minutes=self.lockout_minutes)
            self._attempts[identifier] = [
                ts for ts in self._attempts[identifier]
                if ts > window_start
            ]
        else:
            self._attempts[identifier] = []
        
        # Record this attempt
        self._attempts[identifier].append(now)
        
        # Check if should lock
        if len(self._attempts[identifier]) >= self.max_attempts:
            self._locked[identifier] = now + timedelta(minutes=self.lockout_minutes)
            return True
        
        return False
    
    def is_locked(self, identifier: str) -> bool:
        """Check if account is locked"""
        if identifier not in self._locked:
            return False
        
        if datetime.now() > self._locked[identifier]:
            # Lock expired
            del self._locked[identifier]
            if identifier in self._attempts:
                del self._attempts[identifier]
            return False
        
        return True
    
    def clear(self, identifier: str):
        """Clear lockout on successful login"""
        if identifier in self._attempts:
            del self._attempts[identifier]
        if identifier in self._locked:
            del self._locked[identifier]
    
    def remaining_time(self, identifier: str) -> Optional[int]:
        """Get remaining lockout time in seconds"""
        if identifier not in self._locked:
            return None
        
        remaining = self._locked[identifier] - datetime.now()
        return max(0, int(remaining.total_seconds()))


# =============================================================================
# XSS PROTECTION
# =============================================================================

def escape_html(text: str) -> str:
    """
    Escape HTML special characters to prevent XSS.
    
    Usage:
        safe_text = security.escape_html(user_input)
    """
    if not isinstance(text, str):
        return str(text)
    
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
        .replace("/", "&#x2F;")
    )


def sanitize_html(html: str, allowed_tags: List[str] = None) -> str:
    """
    Remove dangerous HTML tags while keeping safe ones.
    
    Usage:
        safe_html = security.sanitize_html(user_html, allowed_tags=["b", "i", "a"])
    """
    if allowed_tags is None:
        allowed_tags = ["b", "i", "u", "strong", "em", "a", "p", "br"]
    
    # Remove script tags completely
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove on* event handlers
    html = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
    
    # Remove javascript: URLs
    html = re.sub(r'javascript:', '', html, flags=re.IGNORECASE)
    
    # Only keep allowed tags
    pattern = r'<(?!/?({})\b)[^>]*>'.format('|'.join(allowed_tags))
    html = re.sub(pattern, '', html, flags=re.IGNORECASE)
    
    return html


# =============================================================================
# SECURE TOKEN GENERATION
# =============================================================================

def generate_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token"""
    return secrets.token_urlsafe(length)


def generate_api_key() -> str:
    """Generate an API key in format: pyx_xxxxxxxxxxxxxxxx"""
    return f"pyx_{secrets.token_hex(16)}"


# =============================================================================
# ZEN MODE SECURITY CLASS
# =============================================================================

class ZenSecurity:
    """
    Zen Mode Security - Access all security features via security.*
    
    Usage:
        from pyx import security
        
        # Password hashing
        hash = security.hash_password("password123")
        valid = security.verify_password("password123", hash)
        
        # Password policy
        is_valid, errors = security.check_password("weak")
        strength = security.password_strength("MyStr0ng!Pass")
        
        # XSS protection
        safe = security.escape(user_input)
        
        # Tokens
        token = security.generate_token()
        api_key = security.generate_api_key()
        
        # Middlewares
        app.use(security.headers())
        app.use(security.https_redirect())
    """
    
    # Password handling
    hasher = PasswordHasher()
    policy = PasswordPolicy()
    lockout = AccountLockout()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password securely"""
        return PasswordHasher.hash(password)
    
    @staticmethod
    def verify_password(password: str, hash: str) -> bool:
        """Verify password against hash"""
        return PasswordHasher.verify(password, hash)
    
    @staticmethod
    def check_password(password: str) -> tuple:
        """
        Validate password against policy.
        Returns (is_valid, errors)
        """
        return PasswordPolicy().validate(password)
    
    @staticmethod
    def password_strength(password: str) -> dict:
        """Get password strength analysis"""
        return PasswordPolicy().strength(password)
    
    # XSS protection
    @staticmethod
    def escape(text: str) -> str:
        """Escape HTML to prevent XSS"""
        return escape_html(text)
    
    @staticmethod
    def sanitize(html: str, allowed_tags: List[str] = None) -> str:
        """Sanitize HTML keeping only allowed tags"""
        return sanitize_html(html, allowed_tags)
    
    # Token generation
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate secure random token"""
        return generate_token(length)
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate API key"""
        return generate_api_key()
    
    # Middlewares
    @staticmethod
    def headers(hsts: bool = False, csp: str = None) -> SecurityHeaders:
        """Get security headers middleware"""
        return SecurityHeaders(hsts=hsts, csp=csp)
    
    @staticmethod
    def https_redirect() -> HTTPSRedirect:
        """Get HTTPS redirect middleware"""
        return HTTPSRedirect()


# Zen Mode instance
security = ZenSecurity()


__all__ = [
    'security', 'ZenSecurity',
    'PasswordHasher', 'PasswordPolicy', 'AccountLockout',
    'SecurityHeaders', 'HTTPSRedirect',
    'escape_html', 'sanitize_html',
    'generate_token', 'generate_api_key'
]
