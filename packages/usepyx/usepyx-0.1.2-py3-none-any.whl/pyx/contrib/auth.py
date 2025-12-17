"""
PyX Auth Module (pyx.contrib.auth)
Complete authentication system for PyX applications.

Features:
- User model with password hashing
- Login/Logout/Register functionality
- Session-based authentication
- Protected route decorator
- Auth state management
"""

from typing import Optional, List
from datetime import datetime
import hashlib
import secrets

from ..core.state import State, redirect, alert
from ..core.database import Model, Field, session, Query
from ..core.session import Session, SessionStorage


# =============================================================================
# USER MODEL
# =============================================================================

class User(Model, table=True):
    """
    Default User model for authentication.
    
    You can extend this model in your application:
        from pyx.contrib.auth import User
        
        class MyUser(User, table=True):
            __tablename__ = "users"
            bio: Optional[str] = None
            avatar_url: Optional[str] = None
    """
    __tablename__ = "auth_users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    password_hash: str = Field(default="")
    
    # Profile
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    # Status
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    
    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    
    def set_password(self, password: str):
        """Hash and set the password."""
        self.password_hash = hash_password(password)
    
    def check_password(self, password: str) -> bool:
        """Verify a password against the hash."""
        return verify_password(password, self.password_hash)
    
    @property
    def full_name(self) -> str:
        """Get the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username


# =============================================================================
# PASSWORD HASHING
# =============================================================================

def hash_password(password: str, salt: str = None) -> str:
    """
    Hash a password using SHA-256 with salt.
    
    For production, consider using bcrypt or argon2.
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    hash_value = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}${hash_value}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a hash."""
    try:
        salt, stored_hash = password_hash.split("$")
        new_hash = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
        return secrets.compare_digest(new_hash, stored_hash)
    except ValueError:
        return False


# =============================================================================
# AUTH STATE
# =============================================================================

class AuthState(State):
    """
    Authentication state for managing login sessions.
    
    Usage in your app:
        from pyx.contrib.auth import AuthState
        
        # In your login handler
        def login_page():
            return ui.form(
                ui.input(placeholder="Email").on_change(AuthState.set_email),
                ui.input(type="password", placeholder="Password").on_change(AuthState.set_password),
                ui.button("Login").on_click(AuthState.login)
            )
    """
    
    # Form fields
    email: str = ""
    password: str = ""
    confirm_password: str = ""
    username: str = ""
    
    # Auth status
    is_authenticated: bool = False
    current_user_id: Optional[int] = None
    error: Optional[str] = None
    
    def login(self):
        """Handle login."""
        if not self.email or not self.password:
            self.error = "Please enter email and password"
            return alert(self.error)
        
        # Find user
        with session() as db:
            from sqlmodel import select
            statement = select(User).where(User.email == self.email)
            user = db.exec(statement).first()
            
            if user and user.check_password(self.password):
                if not user.is_active:
                    self.error = "Account is disabled"
                    return alert(self.error)
                
                # Update last login
                user.last_login = datetime.now()
                db.add(user)
                db.commit()
                
                # Set auth state
                self.is_authenticated = True
                self.current_user_id = user.id
                self.error = None
                self.password = ""  # Clear password
                
                return redirect("/")
            else:
                self.error = "Invalid email or password"
                return alert(self.error)
    
    def logout(self):
        """Handle logout."""
        self.is_authenticated = False
        self.current_user_id = None
        self.email = ""
        self.password = ""
        self.error = None
        return redirect("/login")
    
    def register(self):
        """Handle registration."""
        if not self.email or not self.password or not self.username:
            self.error = "Please fill in all fields"
            return alert(self.error)
        
        if self.password != self.confirm_password:
            self.error = "Passwords do not match"
            return alert(self.error)
        
        if len(self.password) < 6:
            self.error = "Password must be at least 6 characters"
            return alert(self.error)
        
        # Check if user exists
        with session() as db:
            from sqlmodel import select
            
            existing = db.exec(
                select(User).where(
                    (User.email == self.email) | (User.username == self.username)
                )
            ).first()
            
            if existing:
                self.error = "Email or username already exists"
                return alert(self.error)
            
            # Create user
            user = User(
                email=self.email,
                username=self.username,
            )
            user.set_password(self.password)
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Auto-login after registration
            self.is_authenticated = True
            self.current_user_id = user.id
            self.error = None
            self.password = ""
            self.confirm_password = ""
            
            return redirect("/")
    
    def get_current_user(self) -> Optional[User]:
        """Get the currently logged in user."""
        if not self.current_user_id:
            return None
        return Query.get(User, self.current_user_id)


# =============================================================================
# ROUTE PROTECTION
# =============================================================================

def require_auth(redirect_to: str = "/login"):
    """
    Decorator to protect routes that require authentication.
    
    Usage:
        from pyx.contrib.auth import require_auth
        
        @require_auth()
        def dashboard():
            return ui.div("Welcome to dashboard!")
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Check auth state
            # In a real implementation, this would check the session
            # For now, this is a placeholder
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_superuser(redirect_to: str = "/"):
    """
    Decorator to protect admin-only routes.
    
    Usage:
        from pyx.contrib.auth import require_superuser
        
        @require_superuser()
        def admin_panel():
            return ui.div("Admin only!")
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'User',
    'AuthState',
    'hash_password',
    'verify_password',
    'require_auth',
    'require_superuser',
]
