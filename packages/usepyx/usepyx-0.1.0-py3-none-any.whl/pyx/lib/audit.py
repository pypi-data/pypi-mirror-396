"""
PyX Audit Logging System
Enterprise-grade activity tracking.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from ..data.database import Model, Column, db
import json

# ==========================================
# MODELS
# ==========================================

class AuditLog(Model, table=True):
    """
    Records significant user activities.
    """
    __tablename__ = "pyx_audit_logs"
    
    id: Optional[int] = Column(primary_key=True)
    user_id: Optional[int] = Column(index=True) # Who did it?
    user_email: Optional[str] = None # Capture email in case user is deleted
    action: str = Column(index=True) # What did they do? (e.g. "product.create")
    target_type: Optional[str] = None # e.g. "Product"
    target_id: Optional[str] = None # e.g. "101"
    details: str = Column(default="{}") # JSON blob for extra context
    ip_address: Optional[str] = None
    created_at: datetime = Column(default=datetime.now())

    @property
    def meta(self) -> Dict[str, Any]:
        """Parse details JSON safely"""
        try:
            return json.loads(self.details)
        except:
            return {}

# ==========================================
# ENGINE
# ==========================================

class Audit:
    @staticmethod
    def log(action: str, target: Any = None, details: dict = None, user = None):
        """
        Log an activity.
        
        Args:
            action: String identifier (e.g. "login.success")
            target: The object being acted upon (optional)
            details: Extra dictionary data
            user: Explicit user object (optional, auto-detects from Auth otherwise)
        """
        from .auth import auth
        
        # Auto-detect User
        if not user:
            user = auth.current_user()
            
        user_id = user.id if user else None
        user_email = user.email if user else "anonymous"
        
        # Auto-detect Target info
        target_type = None
        target_id = None
        if target:
            target_type = target.__class__.__name__
            if hasattr(target, 'id'):
                target_id = str(target.id)
                
        # Create Log
        log_entry = AuditLog(
            user_id=user_id,
            user_email=user_email,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=json.dumps(details or {})
        )
        
        try:
            db.save(log_entry)
            print(f"📝 [Audit] {action} by {user_email}")
        except Exception as e:
            print(f"⚠️ [Audit] Failed to save log: {e}")

# ==========================================
# DECORATOR
# ==========================================

from functools import wraps

def track_activity(action: str):
    """
    Decorator to automatically log controller actions.
    
    Usage:
        @track_activity("product.delete")
        def delete_product(id):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Run the actual function first
            result = func(*args, **kwargs)
            
            # Log after success
            # We try to grab the first argument if it might be an ID or Model, just a guess
            target = None
            if args:
                target = args[0] # Naive guess
                
            Audit.log(action, target=target, details={"args": str(args), "kwargs": str(kwargs)})
            
            return result
        return wrapper
    return decorator
