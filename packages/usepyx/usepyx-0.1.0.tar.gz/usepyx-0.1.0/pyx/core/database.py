"""
PyX Database Layer
Wrapper around SQLModel for database operations.

Inspired by Reflex's database pattern:
- rx.Model for table definitions
- rx.session() for queries
- Alembic for migrations
"""

from typing import Any, Dict, Optional, Type, TypeVar, List, Generator
from contextlib import contextmanager
from sqlmodel import SQLModel, Field, Session, create_engine, select
from sqlmodel import Column, String, Integer, Boolean, DateTime, Float, Text
from sqlalchemy.engine import Engine
import os

# Type variable for Model subclasses
T = TypeVar('T', bound='Model')


class Model(SQLModel):
    """
    Base Model class for PyX database tables.
    
    Usage:
        class User(Model, table=True):
            id: Optional[int] = Field(default=None, primary_key=True)
            username: str = Field(index=True)
            email: str = Field(unique=True)
            is_active: bool = Field(default=True)
    
    All SQLModel features are available.
    """
    pass


class DatabaseConfig:
    """Database configuration singleton."""
    
    _engine: Optional[Engine] = None
    _db_url: str = "sqlite:///pyx.db"
    
    @classmethod
    def configure(cls, db_url: str):
        """
        Configure the database URL.
        
        Args:
            db_url: SQLAlchemy database URL
                Examples:
                - sqlite:///myapp.db
                - postgresql://user:pass@localhost/mydb
                - mysql://user:pass@localhost/mydb
        """
        cls._db_url = db_url
        cls._engine = None  # Reset engine to use new URL
    
    @classmethod
    def get_engine(cls) -> Engine:
        """Get or create the database engine."""
        if cls._engine is None:
            cls._engine = create_engine(
                cls._db_url,
                echo=os.getenv("PYX_DB_ECHO", "false").lower() == "true"
            )
        return cls._engine
    
    @classmethod
    def create_tables(cls):
        """Create all tables defined by Model subclasses."""
        SQLModel.metadata.create_all(cls.get_engine())
    
    @classmethod
    def drop_tables(cls):
        """Drop all tables. USE WITH CAUTION!"""
        SQLModel.metadata.drop_all(cls.get_engine())


@contextmanager
def session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Usage:
        from pyx import session, Model
        
        class User(Model, table=True):
            id: Optional[int] = Field(default=None, primary_key=True)
            username: str
        
        # Create
        with session() as db:
            user = User(username="admin")
            db.add(user)
            db.commit()
        
        # Read
        with session() as db:
            users = db.exec(select(User)).all()
    """
    engine = DatabaseConfig.get_engine()
    with Session(engine) as db:
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise


class Query:
    """
    Helper class for common query patterns.
    
    Usage:
        from pyx import Query, Model
        
        class User(Model, table=True):
            id: Optional[int] = Field(default=None, primary_key=True)
            username: str
        
        # Get all
        users = Query(User).all()
        
        # Get by ID
        user = Query(User).get(1)
        
        # Filter
        admins = Query(User).filter(User.is_admin == True).all()
    """
    
    def __init__(self, model: Type[T]):
        self.model = model
        self._statement = select(model)
    
    def filter(self, *conditions) -> 'Query':
        """Add filter conditions."""
        for condition in conditions:
            self._statement = self._statement.where(condition)
        return self
    
    def order_by(self, *columns) -> 'Query':
        """Add ordering."""
        self._statement = self._statement.order_by(*columns)
        return self
    
    def limit(self, count: int) -> 'Query':
        """Limit results."""
        self._statement = self._statement.limit(count)
        return self
    
    def offset(self, count: int) -> 'Query':
        """Offset results."""
        self._statement = self._statement.offset(count)
        return self
    
    def all(self) -> List[T]:
        """Execute and return all results."""
        with session() as db:
            return list(db.exec(self._statement).all())
    
    def first(self) -> Optional[T]:
        """Execute and return first result."""
        with session() as db:
            return db.exec(self._statement).first()
    
    def one(self) -> T:
        """Execute and return exactly one result. Raises if not found."""
        with session() as db:
            return db.exec(self._statement).one()
    
    def count(self) -> int:
        """Return count of results."""
        # Simple implementation - could be optimized
        return len(self.all())
    
    @classmethod
    def get(cls, model: Type[T], id: Any) -> Optional[T]:
        """Get a record by primary key."""
        with session() as db:
            return db.get(model, id)
    
    @classmethod
    def create(cls, model: Type[T], **data) -> T:
        """Create a new record."""
        with session() as db:
            instance = model(**data)
            db.add(instance)
            db.commit()
            db.refresh(instance)
            return instance
    
    @classmethod
    def update(cls, instance: T, **data) -> T:
        """Update a record."""
        with session() as db:
            for key, value in data.items():
                setattr(instance, key, value)
            db.add(instance)
            db.commit()
            db.refresh(instance)
            return instance
    
    @classmethod
    def delete(cls, instance: T) -> None:
        """Delete a record."""
        with session() as db:
            db.delete(instance)
            db.commit()


# Convenience function
def configure_db(db_url: str):
    """
    Configure database connection.
    
    Example:
        from pyx import configure_db
        
        # SQLite (default)
        configure_db("sqlite:///myapp.db")
        
        # PostgreSQL
        configure_db("postgresql://user:pass@localhost/mydb")
    """
    DatabaseConfig.configure(db_url)


def create_tables():
    """Create all defined database tables."""
    DatabaseConfig.create_tables()


# Export
__all__ = [
    'Model',
    'Field',
    'session',
    'Query',
    'configure_db',
    'create_tables',
    'DatabaseConfig',
    # Re-export SQLModel types for convenience
    'Column',
    'String',
    'Integer',
    'Boolean',
    'DateTime',
    'Float',
    'Text',
    'select',
]
