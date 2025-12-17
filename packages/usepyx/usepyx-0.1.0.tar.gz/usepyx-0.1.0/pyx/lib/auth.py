"""
PyX Auth System
Built-in authentication with Users, Sessions, and Roles.
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional, List
from ..data.database import Model, Column, db
from ..core.security import security, PasswordHasher, AccountLockout


# ==========================================
# MODELS
# ==========================================

class User(Model, table=True):
    """
    Built-in User model for authentication.
    """
    __tablename__ = "pyx_users"
    
    id: Optional[int] = Column(primary_key=True)
    email: str = Column(unique=True, index=True)
    password_hash: str
    full_name: str = Column(default="User")
    role: str = Column(default="user")  # user, admin, editor
    is_active: bool = True
    created_at: datetime = Column(default=datetime.now())
    last_login: Optional[datetime] = None
    
    @property
    def permissions(self) -> List[str]:
        """
        Get permissions based on role. 
        In the future, this can load from a Roles table.
        """
        # Default Hardcoded Roles for now (Zen Mode)
        ROLES = {
            "admin": ["*"],
            "editor": ["view", "create", "update"],
            "user": ["view"]
        }
        return ROLES.get(self.role, [])

    def can(self, permission: str) -> bool:
        """Check if user has specific permission"""
        perms = self.permissions
        if "*" in perms: return True
        return permission in perms

    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = Auth.hash_password(password)
    
    def check_password(self, password: str) -> bool:
        """Verify password"""
        return Auth.verify_password(password, self.password_hash)
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Session(Model, table=True):
    """
    User session for tracking logged-in users.
    """
    __tablename__ = "pyx_sessions"
    
    id: Optional[int] = Column(primary_key=True)
    user_id: int
    token: str = Column(unique=True, index=True)
    expires_at: datetime
    created_at: datetime = Column(default=datetime.now())
    
    @property
    def is_valid(self) -> bool:
        return datetime.now() < self.expires_at


# ==========================================
# AUTH ENGINE
# ==========================================

class Auth:
    """
    PyX Authentication Engine.
    
    Usage:
        from pyx.auth import auth, User
        
        # Setup
        auth.init()
        
        # Register
        user = auth.register("email@example.com", "password123", "John Doe")
        
        # Login
        session = auth.login("email@example.com", "password123")
        
        # Get current user
        user = auth.current_user(session_token)
        
        # Logout
        auth.logout(session_token)
    """
    
    _current_session: Optional[Session] = None
    _current_user: Optional[User] = None
    
    # ==========================================
    # PASSWORD UTILITIES
    # ==========================================
    
    # Account lockout for brute force protection
    _lockout = AccountLockout(max_attempts=5, lockout_minutes=15)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password securely using bcrypt (or PBKDF2 fallback)"""
        return security.hash_password(password)
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return security.verify_password(password, password_hash)
    
    @staticmethod
    def check_password_strength(password: str) -> dict:
        """Check password strength and get suggestions"""
        return security.password_strength(password)
    
    @staticmethod
    def validate_password(password: str) -> tuple:
        """Validate password meets policy requirements. Returns (is_valid, errors)"""
        return security.check_password(password)
    
    # ==========================================
    # USER MANAGEMENT
    # ==========================================
    
    @staticmethod
    def init():
        """Initialize auth tables"""
        db.init()
        print("[PyX Auth] Tables initialized")
    
    @staticmethod
    def register(email: str, password: str, full_name: str = "User", role: str = "user") -> Optional[User]:
        """
        Register a new user.
        
        Returns:
            User object if successful, None if email already exists.
        """
        # Check if email exists
        existing = db.find_by(User, email=email)
        if existing:
            print(f"[PyX Auth] Registration failed: {email} already exists")
            return None
        
        # Create user
        user = User(
            email=email,
            full_name=full_name,
            role=role
        )
        user.set_password(password)
        
        db.save(user)
        print(f"[PyX Auth] User registered: {email}")
        return user
    
    @staticmethod
    def login(email: str, password: str, remember: bool = False) -> Optional[str]:
        """
        Authenticate user and create session.
        
        Args:
            email: User email
            password: Plain text password
            remember: If True, session lasts 30 days, else 24 hours
            
        Returns:
            Session token if successful, None if failed.
        """
        user = db.find_by(User, email=email)
        
        if not user:
            print(f"[PyX Auth] Login failed: User not found")
            return None
        
        if not user.is_active:
            print(f"[PyX Auth] Login failed: User is inactive")
            return None
        
        if not user.check_password(password):
            print(f"[PyX Auth] Login failed: Wrong password")
            return None
        
        # Create session
        token = secrets.token_urlsafe(32)
        expires_in = timedelta(days=30) if remember else timedelta(hours=24)
        
        session = Session(
            user_id=user.id,
            token=token,
            expires_at=datetime.now() + expires_in
        )
        db.save(session)
        
        # Update last login
        user.last_login = datetime.now()
        db.save(user)
        
        # Store in memory
        Auth._current_session = session
        Auth._current_user = user
        
        print(f"[PyX Auth] Login success: {email}")
        return token
    
    @staticmethod
    def logout(token: str = None) -> bool:
        """
        End user session.
        
        Args:
            token: Session token (optional, uses current session if not provided)
        """
        if token:
            session = db.find_by(Session, token=token)
        else:
            session = Auth._current_session
        
        if session:
            db.delete(session)
            Auth._current_session = None
            Auth._current_user = None
            print("[PyX Auth] Logout success")
            return True
        
        return False
    
    @staticmethod
    def get_user(token: str) -> Optional[User]:
        """
        Get user from session token.
        
        Args:
            token: Session token
            
        Returns:
            User object if valid session, None otherwise.
        """
        session = db.find_by(Session, token=token)
        
        if not session:
            return None
        
        if not session.is_valid:
            db.delete(session)  # Clean up expired session
            return None
        
        return db.find_by_id(User, session.user_id)
    
    @staticmethod
    def current_user() -> Optional[User]:
        """Get currently logged in user (from memory)"""
        return Auth._current_user
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is logged in"""
        return Auth._current_user is not None
    
    @staticmethod
    def require_auth(func):
        """
        Decorator to protect routes.
        
        Usage:
            @auth.require_auth
            def dashboard_page():
                user = auth.current_user()
                ...
        """
        def wrapper(*args, **kwargs):
            if not Auth.is_authenticated():
                print("[PyX Auth] Access denied: Not authenticated")
                # TODO: Redirect to login page
                return None
            return func(*args, **kwargs)
        return wrapper
    
    @staticmethod
    def require_role(role: str):
        """
        Decorator to protect routes by role.
        
        Usage:
            @auth.require_role("admin")
            def admin_page():
                ...
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                user = Auth.current_user()
                if not user:
                    print("[PyX Auth] Access denied: Not authenticated")
                    return None
                if user.role != role:
                    print(f"[PyX Auth] Access denied: Requires role '{role}'")
                    return None
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    # ==========================================
    # USER QUERIES
    # ==========================================
    
    @staticmethod
    def get_all_users() -> List[User]:
        """Get all users"""
        return db.find_all(User)
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Find user by email"""
        return db.find_by(User, email=email)
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Find user by ID"""
        return db.find_by_id(User, user_id)
    
    @staticmethod
    def update_user(user: User) -> User:
        """Update user data"""
        return db.save(user)
    
    @staticmethod
    def delete_user(user: User) -> None:
        """Delete user and their sessions"""
        # Delete all user sessions first
        sessions = db.find_many(Session, user_id=user.id)
        for session in sessions:
            db.delete(session)
        db.delete(user)
        print(f"[PyX Auth] User deleted: {user.email}")


# Global auth instance
auth = Auth()
