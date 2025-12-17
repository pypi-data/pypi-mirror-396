"""
PyX Database Layer
Full ORM with Relationships support.
"""
from sqlmodel import SQLModel, Field, Session, create_engine, select, Relationship as SQLRelationship
from typing import Optional, List, Any, Type, TYPE_CHECKING
from datetime import datetime

# --- RE-EXPORT WRAPPER (Agar user coding ala PyX) ---
class Model(SQLModel):
    """
    Base Model untuk semua tabel PyX.
    
    Usage:
        class User(Model, table=True):
            id: int = Column(primary_key=True)
            name: str
            email: str = Column(unique=True)
            
            # Relationships
            posts: List["Post"] = Relationship(back_populates="author")
    """
    pass


def Column(
    default=None, 
    primary_key=False, 
    unique=False, 
    index=False,
    nullable=True,
    foreign_key=None
):
    """
    Column definition helper.
    
    Usage:
        id: int = Column(primary_key=True)
        name: str = Column()
        email: str = Column(unique=True, index=True)
        author_id: int = Column(foreign_key="user.id")
    """
    return Field(
        default=default, 
        primary_key=primary_key, 
        unique=unique, 
        index=index,
        nullable=nullable,
        foreign_key=foreign_key
    )


def Relationship(back_populates=None, link_model=None, sa_relationship_kwargs=None):
    """
    Relationship definition helper.
    
    Usage:
        # One-to-Many (User has many Posts)
        class User(Model, table=True):
            posts: List["Post"] = Relationship(back_populates="author")
        
        # Many-to-One (Post belongs to User)
        class Post(Model, table=True):
            author_id: int = Column(foreign_key="user.id")
            author: "User" = Relationship(back_populates="posts")
        
        # Many-to-Many (with link table)
        class UserRole(Model, table=True):
            user_id: int = Column(foreign_key="user.id", primary_key=True)
            role_id: int = Column(foreign_key="role.id", primary_key=True)
        
        class User(Model, table=True):
            roles: List["Role"] = Relationship(back_populates="users", link_model=UserRole)
    """
    kwargs = sa_relationship_kwargs or {}
    if link_model:
        kwargs["secondary"] = link_model.__tablename__ if hasattr(link_model, '__tablename__') else None
    return SQLRelationship(back_populates=back_populates, sa_relationship_kwargs=kwargs if kwargs else None)


# Common column types
def PrimaryKey():
    """Auto-increment primary key"""
    return Column(primary_key=True, default=None)

def ForeignKey(table_column: str):
    """Foreign key reference"""
    return Column(foreign_key=table_column)

def CreatedAt():
    """Auto-set creation timestamp"""
    return Field(default_factory=datetime.utcnow)

def UpdatedAt():
    """Auto-update timestamp"""
    return Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})


class Database:
    """
    PyX Database Engine
    Full-featured ORM with relationships.
    
    Usage:
        from pyx import db, Model, Column, Relationship
        
        class User(Model, table=True):
            id: int = Column(primary_key=True)
            name: str
            posts: List["Post"] = Relationship(back_populates="author")
        
        class Post(Model, table=True):
            id: int = Column(primary_key=True)
            title: str
            author_id: int = Column(foreign_key="user.id")
            author: User = Relationship(back_populates="posts")
        
        db.init()
        
        # Create with relationship
        user = User(name="John")
        db.save(user)
        
        post = Post(title="Hello", author_id=user.id)
        db.save(post)
        
        # Query with relationship
        user = db.find_by_id(User, 1)
        print(user.posts)  # [Post(...)]
    """
    
    def __init__(self, url: str = "sqlite:///database.db"):
        self.url = url
        self.engine = None
        self._session = None
        
    def connect(self, url: str = None):
        """Initialize database engine"""
        if url:
            self.url = url
        self.engine = create_engine(self.url, echo=False)
        return self
    
    def init(self):
        """Create all tables from registered Models"""
        if not self.engine:
            self.connect()
        SQLModel.metadata.create_all(self.engine)
        print(f"[PyX DB] Tables created: {self.url}")
        return self
    
    # Alias
    create_all = init
    
    def session(self) -> Session:
        """Get database session"""
        if not self.engine:
            self.connect()
        return Session(self.engine)
    
    # =========================================================================
    # CRUD Operations
    # =========================================================================
    
    def save(self, obj: Model) -> Model:
        """Insert or Update object to database"""
        with self.session() as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj
    
    def save_all(self, objects: List[Model]) -> List[Model]:
        """Bulk insert/update"""
        with self.session() as session:
            for obj in objects:
                session.add(obj)
            session.commit()
            for obj in objects:
                session.refresh(obj)
            return objects
    
    def delete(self, obj: Model) -> None:
        """Remove object from database"""
        with self.session() as session:
            session.delete(obj)
            session.commit()
    
    def delete_by_id(self, model: type, id: int) -> bool:
        """Delete by ID"""
        obj = self.find_by_id(model, id)
        if obj:
            self.delete(obj)
            return True
        return False
    
    # =========================================================================
    # Query Operations
    # =========================================================================
    
    def find_all(self, model: type) -> List[Any]:
        """Get all records"""
        with self.session() as session:
            return session.exec(select(model)).all()
    
    # Alias
    all = find_all
            
    def find_by_id(self, model: type, id: int) -> Optional[Any]:
        """Find by primary key"""
        with self.session() as session:
            return session.get(model, id)
    
    # Alias
    get = find_by_id
            
    def find_by(self, model: type, **kwargs) -> Optional[Any]:
        """Find first match"""
        with self.session() as session:
            statement = select(model)
            for key, value in kwargs.items():
                statement = statement.where(getattr(model, key) == value)
            return session.exec(statement).first()
    
    # Alias
    first = find_by
    
    def find_many(self, model: type, **kwargs) -> List[Any]:
        """Find all matches"""
        with self.session() as session:
            statement = select(model)
            for key, value in kwargs.items():
                statement = statement.where(getattr(model, key) == value)
            return session.exec(statement).all()
    
    # Alias
    filter = find_many
    where = find_many
    
    def count(self, model: type, **kwargs) -> int:
        """Count records"""
        if kwargs:
            return len(self.find_many(model, **kwargs))
        return len(self.find_all(model))
    
    def exists(self, model: type, **kwargs) -> bool:
        """Check if record exists"""
        return self.find_by(model, **kwargs) is not None
    
    # =========================================================================
    # Advanced Queries
    # =========================================================================
    
    def query(self, model: type) -> "QueryBuilder":
        """Start a query builder"""
        return QueryBuilder(self, model)
    
    def raw(self, sql: str, params: dict = None):
        """Execute raw SQL"""
        with self.session() as session:
            result = session.exec(sql, params or {})
            return result.all()
    
    # =========================================================================
    # EAGER LOADING (Solve N+1 Problem)
    # =========================================================================
    
    def with_relations(self, model: type, *relations: str) -> List[Any]:
        """
        Eager load relationships to avoid N+1 problem.
        
        Usage:
            # N+1 Problem (BAD - 1 query + N queries for each user's posts):
            users = db.find_all(User)
            for user in users:
                print(user.posts)  # Each access = 1 query!
            
            # Eager Loading (GOOD - just 2 queries total):
            users = db.with_relations(User, "posts")
            for user in users:
                print(user.posts)  # Already loaded!
            
            # Multiple relations:
            users = db.with_relations(User, "posts", "comments", "profile")
        """
        from sqlalchemy.orm import selectinload, joinedload
        
        with self.session() as session:
            statement = select(model)
            
            for relation in relations:
                # Use selectinload for collections, joinedload for single
                rel_attr = getattr(model, relation, None)
                if rel_attr:
                    statement = statement.options(selectinload(rel_attr))
            
            return session.exec(statement).all()
    
    def eager(self, model: type) -> "EagerQueryBuilder":
        """
        Start an eager loading query.
        
        Usage:
            users = db.eager(User).load("posts", "comments").where(active=True).all()
        """
        return EagerQueryBuilder(self, model)
    
    # =========================================================================
    # MIGRATIONS
    # =========================================================================
    
    def migrate(self, direction: str = "up"):
        """
        Run migrations.
        
        Usage:
            db.migrate("up")    # Apply migrations
            db.migrate("down")  # Rollback last migration
        """
        migrator = Migrator(self)
        if direction == "up":
            migrator.up()
        elif direction == "down":
            migrator.down()
        return self
    
    def make_migration(self, name: str):
        """
        Create a new migration file.
        
        Usage:
            db.make_migration("add_users_table")
            # Creates: migrations/20231214_120000_add_users_table.py
        """
        migrator = Migrator(self)
        migrator.create(name)
        return self
    
    def migration_status(self) -> List[dict]:
        """Get migration status"""
        migrator = Migrator(self)
        return migrator.status()


class EagerQueryBuilder:
    """
    Query builder with eager loading support.
    
    Usage:
        users = db.eager(User)
            .load("posts", "comments")
            .where(active=True)
            .order_by("name")
            .all()
    """
    
    def __init__(self, db: "Database", model: type):
        self.db = db
        self.model = model
        self._relations = []
        self._filters = {}
        self._order = None
        self._order_desc = False
        self._limit_val = None
        self._offset_val = None
    
    def load(self, *relations: str) -> "EagerQueryBuilder":
        """Specify relations to eager load"""
        self._relations.extend(relations)
        return self
    
    def where(self, **kwargs) -> "EagerQueryBuilder":
        """Filter conditions"""
        self._filters.update(kwargs)
        return self
    
    def order_by(self, field: str, desc: bool = False) -> "EagerQueryBuilder":
        """Order results"""
        self._order = field
        self._order_desc = desc
        return self
    
    def limit(self, val: int) -> "EagerQueryBuilder":
        """Limit results"""
        self._limit_val = val
        return self
    
    def offset(self, val: int) -> "EagerQueryBuilder":
        """Offset results"""
        self._offset_val = val
        return self
    
    def all(self) -> List[Any]:
        """Execute query with eager loading"""
        from sqlalchemy.orm import selectinload
        
        with self.db.session() as session:
            statement = select(self.model)
            
            # Eager load relations
            for relation in self._relations:
                rel_attr = getattr(self.model, relation, None)
                if rel_attr:
                    statement = statement.options(selectinload(rel_attr))
            
            # Apply filters
            for key, value in self._filters.items():
                statement = statement.where(getattr(self.model, key) == value)
            
            # Order
            if self._order:
                col = getattr(self.model, self._order)
                statement = statement.order_by(col.desc() if self._order_desc else col)
            
            # Limit/Offset
            if self._limit_val:
                statement = statement.limit(self._limit_val)
            if self._offset_val:
                statement = statement.offset(self._offset_val)
            
            return session.exec(statement).all()
    
    def first(self) -> Optional[Any]:
        """Get first result"""
        results = self.limit(1).all()
        return results[0] if results else None


class Migrator:
    """
    Database Migration System.
    
    Usage:
        # Via CLI:
        pyx migrate up
        pyx migrate down
        pyx migrate make add_users_table
        pyx migrate status
        
        # Or programmatically:
        from pyx import db
        db.make_migration("add_posts_table")
        db.migrate("up")
    """
    
    MIGRATIONS_DIR = "migrations"
    MIGRATIONS_TABLE = "_pyx_migrations"
    
    def __init__(self, db: "Database"):
        self.db = db
        self._ensure_migrations_dir()
        self._ensure_migrations_table()
    
    def _ensure_migrations_dir(self):
        """Create migrations directory if not exists"""
        import os
        if not os.path.exists(self.MIGRATIONS_DIR):
            os.makedirs(self.MIGRATIONS_DIR)
            # Create __init__.py
            with open(f"{self.MIGRATIONS_DIR}/__init__.py", "w") as f:
                f.write("# PyX Migrations\n")
    
    def _ensure_migrations_table(self):
        """Create migrations tracking table"""
        if not self.db.engine:
            self.db.connect()
        
        with self.db.session() as session:
            session.exec(f"""
                CREATE TABLE IF NOT EXISTS {self.MIGRATIONS_TABLE} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            session.commit()
    
    def create(self, name: str):
        """Create a new migration file"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.py"
        filepath = f"{self.MIGRATIONS_DIR}/{filename}"
        
        template = f'''"""
Migration: {name}
Created: {datetime.now().isoformat()}
"""
from pyx import db


def up():
    """Apply migration"""
    # Example:
    # db.raw("""
    #     CREATE TABLE users (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         name VARCHAR(255),
    #         email VARCHAR(255) UNIQUE
    #     )
    # """)
    pass


def down():
    """Rollback migration"""
    # Example:
    # db.raw("DROP TABLE users")
    pass
'''
        
        with open(filepath, "w") as f:
            f.write(template)
        
        print(f"[PyX Migration] Created: {filepath}")
        return filepath
    
    def up(self):
        """Apply pending migrations"""
        import os
        import importlib.util
        
        applied = self._get_applied()
        
        migrations = sorted([
            f for f in os.listdir(self.MIGRATIONS_DIR)
            if f.endswith(".py") and f != "__init__.py"
        ])
        
        for migration in migrations:
            name = migration[:-3]  # Remove .py
            if name not in applied:
                print(f"[PyX Migration] Applying: {name}")
                
                # Load and run migration
                spec = importlib.util.spec_from_file_location(
                    name, f"{self.MIGRATIONS_DIR}/{migration}"
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, "up"):
                    module.up()
                
                # Record migration
                self._record_migration(name)
                print(f"[PyX Migration] Applied: {name}")
        
        if not any(m[:-3] not in applied for m in migrations):
            print("[PyX Migration] Nothing to migrate.")
    
    def down(self):
        """Rollback last migration"""
        import importlib.util
        
        applied = self._get_applied()
        if not applied:
            print("[PyX Migration] Nothing to rollback.")
            return
        
        last = applied[-1]
        migration_file = None
        
        import os
        for f in os.listdir(self.MIGRATIONS_DIR):
            if f.startswith(last) or f[:-3] == last:
                migration_file = f
                break
        
        if migration_file:
            print(f"[PyX Migration] Rolling back: {last}")
            
            spec = importlib.util.spec_from_file_location(
                last, f"{self.MIGRATIONS_DIR}/{migration_file}"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, "down"):
                module.down()
            
            self._remove_migration(last)
            print(f"[PyX Migration] Rolled back: {last}")
    
    def status(self) -> List[dict]:
        """Get migration status"""
        import os
        
        applied = set(self._get_applied())
        
        migrations = sorted([
            f[:-3] for f in os.listdir(self.MIGRATIONS_DIR)
            if f.endswith(".py") and f != "__init__.py"
        ])
        
        result = []
        for m in migrations:
            result.append({
                "name": m,
                "applied": m in applied
            })
        
        return result
    
    def _get_applied(self) -> List[str]:
        """Get list of applied migrations"""
        try:
            with self.db.session() as session:
                result = session.exec(
                    f"SELECT name FROM {self.MIGRATIONS_TABLE} ORDER BY id"
                )
                return [r[0] for r in result.all()]
        except:
            return []
    
    def _record_migration(self, name: str):
        """Record migration as applied"""
        with self.db.session() as session:
            session.exec(
                f"INSERT INTO {self.MIGRATIONS_TABLE} (name) VALUES (:name)",
                {"name": name}
            )
            session.commit()
    
    def _remove_migration(self, name: str):
        """Remove migration record"""
        with self.db.session() as session:
            session.exec(
                f"DELETE FROM {self.MIGRATIONS_TABLE} WHERE name = :name",
                {"name": name}
            )
            session.commit()


class QueryBuilder:
    """
    Chainable query builder.
    
    Usage:
        users = db.query(User)
            .where(active=True)
            .order_by("name")
            .limit(10)
            .offset(20)
            .all()
    """
    
    def __init__(self, db: Database, model: type):
        self.db = db
        self.model = model
        self._filters = {}
        self._order = None
        self._order_desc = False
        self._limit_val = None
        self._offset_val = None
    
    def where(self, **kwargs) -> "QueryBuilder":
        """Add filter conditions"""
        self._filters.update(kwargs)
        return self
    
    def order_by(self, field: str, desc: bool = False) -> "QueryBuilder":
        """Order results"""
        self._order = field
        self._order_desc = desc
        return self
    
    def limit(self, val: int) -> "QueryBuilder":
        """Limit results"""
        self._limit_val = val
        return self
    
    def offset(self, val: int) -> "QueryBuilder":
        """Offset results"""
        self._offset_val = val
        return self
    
    def all(self) -> List[Any]:
        """Execute and return all results"""
        with self.db.session() as session:
            statement = select(self.model)
            
            # Apply filters
            for key, value in self._filters.items():
                statement = statement.where(getattr(self.model, key) == value)
            
            # Apply order
            if self._order:
                col = getattr(self.model, self._order)
                statement = statement.order_by(col.desc() if self._order_desc else col)
            
            # Apply limit/offset
            if self._limit_val:
                statement = statement.limit(self._limit_val)
            if self._offset_val:
                statement = statement.offset(self._offset_val)
            
            return session.exec(statement).all()
    
    def first(self) -> Optional[Any]:
        """Get first result"""
        results = self.limit(1).all()
        return results[0] if results else None
    
    def count(self) -> int:
        """Count results"""
        return len(self.all())
    
    def exists(self) -> bool:
        """Check if any results exist"""
        return self.first() is not None


class ZenDatabase(Database):
    """
    Zen Mode Database - Access everything via db.*
    
    Usage:
        from pyx import db
        
        # Define models using db.Model
        class User(db.Model, table=True):
            id: int = db.Column(primary_key=True)
            name: str
            posts: List["Post"] = db.Relationship(back_populates="author")
        
        class Post(db.Model, table=True):
            id: int = db.Column(primary_key=True)
            title: str
            author_id: int = db.Column(foreign_key="user.id")
            author: User = db.Relationship(back_populates="posts")
        
        # Initialize
        db.init()
        
        # CRUD
        user = User(name="John")
        db.save(user)
    """
    
    # Expose Model and helpers as class attributes
    Model = Model
    
    @staticmethod
    def Column(default=None, primary_key=False, unique=False, index=False, nullable=True, foreign_key=None):
        """Column definition - Zen Mode"""
        return Column(default, primary_key, unique, index, nullable, foreign_key)
    
    @staticmethod
    def Relationship(back_populates=None, link_model=None, sa_relationship_kwargs=None):
        """Relationship definition - Zen Mode"""
        return Relationship(back_populates, link_model, sa_relationship_kwargs)
    
    @staticmethod
    def PrimaryKey():
        """Primary key column - Zen Mode"""
        return PrimaryKey()
    
    @staticmethod
    def ForeignKey(table_column: str):
        """Foreign key column - Zen Mode"""
        return ForeignKey(table_column)
    
    @staticmethod
    def CreatedAt():
        """Created timestamp - Zen Mode"""
        return CreatedAt()
    
    @staticmethod
    def UpdatedAt():
        """Updated timestamp - Zen Mode"""
        return UpdatedAt()


# Global Database Instance (Zen Mode)
db = ZenDatabase()

