# 🚀 PyX Framework

> **"No JavaScript, no HTML mess, just Zen Mode"**  
> The Pure Python Full-Stack Web Framework

PyX adalah framework full-stack yang memungkinkan Anda membangun aplikasi web **100% dengan Python** - tanpa JavaScript, tanpa HTML templates, tanpa context switching.

---

## ✨ Features

| Category | Features |
|----------|----------|
| **🐍 100% Python** | UI, Backend, Database - semua Python |
| **⚡ High Performance** | Granian server (Rust-powered) |
| **🧘 Zen Mode** | Semua via `ui.*`, `db.*` namespace |
| **🎨 100+ Components** | Premium UI components |
| **📡 Real-time** | WebSocket Rooms & Presence |
| **🗄️ Database ORM** | Relationships, Migrations, N+1 solution |
| **🔐 Auth Built-in** | Login, Register, Roles, Security Headers |
| **🤖 AI Ready** | Built-in OpenAI/Claude/Gemini integration |
| **☁️ Cloud Native** | Unified Storage (S3/GCS/Local) |
| **🔋 Batteries** | Email, Jobs, i18n, PWA, SEO, OpenAPI |

---

## 📦 Installation

```bash
# From PyPI
pip install usepyx

# From source
pip install git+https://github.com/sukirman1901/usePyX.git

# For development
git clone https://github.com/sukirman1901/usePyX.git
cd usePyX
pip install -e .
```

---

## 🚀 Quick Start

```bash
# Create project
pyx init myapp
cd myapp

# Run
pyx run
```

Open `http://localhost:8000` 🎉

---

## 🧘 Zen Mode

**Satu import untuk semuanya:**

```python
from pyx import ui, State, var, redirect, Model, Field

# ⚡ State Management
class CounterState(State):
    count: int = 0
    
    @var  # Computed var - auto-recalculates!
    def double(self) -> int:
        return self.count * 2
    
    def increment(self):
        self.count += 1
    
    def reset(self):
        self.count = 0
        return redirect("/")  # Server-driven navigation!

# 🎨 UI with State binding
def counter_page():
    return ui.div(
        ui.h1(f"Count: {CounterState.count}"),
        ui.p(f"Double: {CounterState.double}"),
        ui.button("Add").on_click(CounterState.increment),
        ui.button("Reset").on_click(CounterState.reset),
    ).p(8)

# 🗄️ Database
class User(Model, table=True):
    id: int = Field(primary_key=True)
    name: str
    email: str = Field(unique=True)
```

---

## 🎨 UI Components

### Zen Mode Styling

```python
# Pythonic styling (tidak perlu Tailwind strings)
ui.div("Hello").style(
    bg="blue-500",
    color="white",
    p=4,
    rounded="xl",
    shadow="lg"
)

# Presets
ui.button("Submit").apply(ui.preset("button_primary"))
```

### 100+ Components

```python
# Navigation
ui.navbar(brand=..., items=[...])
ui.sidebar(items=[...])
ui.breadcrumb([...])

# Layout
ui.container(...)
ui.hero(title="...", subtitle="...")
ui.section(title="...", children=...)
ui.footer(...)

# Interaction
ui.modal(trigger=..., content=...)
ui.tabs([...])
ui.accordion([...])

# Data
ui.datagrid(data)
ui.chart(data, type="line")

# Forms
ui.input(placeholder="...")
ui.select(options=[...])
ui.file_upload(accept="image/*")
```

---

## 🗄️ Database ORM

### Relationships

```python
from pyx import db
from typing import List, Optional

class User(db.Model, table=True):
    id: Optional[int] = db.Column(primary_key=True)
    name: str
    posts: List["Post"] = db.Relationship(back_populates="author")

class Post(db.Model, table=True):
    id: Optional[int] = db.Column(primary_key=True)
    title: str
    author_id: int = db.Column(foreign_key="user.id")
    author: User = db.Relationship(back_populates="posts")

db.init()
```

### Queries

```python
# CRUD
user = User(name="John")
db.save(user)
db.delete(user)

# Find
users = db.find_all(User)
user = db.get(User, 1)
user = db.filter(User, active=True)

# Eager loading (N+1 solution)
users = db.with_relations(User, "posts")

# Query builder
users = (
    db.query(User)
    .where(active=True)
    .order_by("name")
    .limit(10)
    .all()
)
```

### Migrations

```bash
pyx generate migration add_users_table
pyx migrate up
pyx migrate down
```

---

## 🔐 Authentication

```python
from pyx.contrib.auth import User, AuthState

# User model with password hashing
user = User(email="admin@pyx.dev", username="admin")
user.set_password("secret123")

# Verify password
if user.check_password("secret123"):
    print("Login successful!")

# AuthState for login/logout flow
class MyAuth(AuthState):
    def login(self):
        # Built-in validation & redirect
        return super().login()

# UI with auth binding
ui.input(placeholder="Email").on_change(MyAuth.set_email)
ui.input(type="password").on_change(MyAuth.set_password)
ui.button("Login").on_click(MyAuth.login)
```

---

## 🛡️ Enterprise Security

PyX is "Secure by Default" with built-in protection against common vulnerabilities.

| Feature | Description |
|---------|-------------|
| **🔐 Bcrypt Hashing** | Auto-salted password hashing |
| **🚦 Rate Limiting** | IP-based request throttling |
| **🛡️ CSRF & XSS** | Built-in protection & sanitization |
| **🔒 Security Headers** | OWASP-recommended headers (HSTS, CSP) |
| **🚫 Brute-force** | Account lockout mechanism |
| **💉 SQL Injection** | Prevented via parameterized queries |


## 🛠️ CLI Commands

### Project Management

```bash
pyx init myapp          # Create new project
pyx run                  # Run development server
pyx build                # Build for production (SSG)
pyx test                 # Run tests
```

### Database Commands (NEW!)

```bash
pyx db init              # Initialize Alembic migrations
pyx db makemigrations    # Generate migration from model changes
pyx db migrate           # Apply pending migrations
pyx db rollback          # Rollback last migration
pyx db history           # Show migration history
pyx db current           # Show current revision
```

### Code Generators

```bash
# Generate model
pyx g model User name:str email:str

# Generate page
pyx g page dashboard

# Generate component
pyx g component UserCard

# Generate API (with CRUD)
pyx g api users --crud

# Generate test
pyx g test users

# Generate migration
pyx g migration add_posts_table
```

---

## 📡 Real-time

```python
from pyx import event

@event("message")
def on_message(data, client):
    broadcast({
        "type": "new_message",
        "text": data["text"]
    })
```

---

## 🔧 Zen Mode Namespaces

```python
# NEW! State Management
from pyx import State, var, redirect, alert, toast

class AppState(State):
    count: int = 0
    
    @var
    def doubled(self) -> int:
        return self.count * 2
    
    def increment(self):
        self.count += 1
        return toast("Incremented!", "success")

# NEW! Background Tasks
from pyx import background, delayed, periodic

@background
async def send_email(user_id):
    # Runs without blocking UI
    await email.send(...)

@periodic(60)
def check_notifications():
    # Runs every 60 seconds
    ...

# Database (NEW API)
from pyx import Model, Field, session, Query, select

class User(Model, table=True):
    id: int = Field(primary_key=True)
    email: str = Field(unique=True)

with session() as db:
    users = db.exec(select(User)).all()

# Session Management
from pyx import Session
session = Session()
session['user_id'] = 123
session.save()

# Auth Module
from pyx.contrib.auth import User, AuthState

# UI (Frontend)
from pyx import ui
ui.button("Click").on_click(AppState.increment)
ui.input().on_change(AppState.set_count)  # Auto-setter!

# Cloud Storage
from pyx import storage
url = storage.upload(file, folder="uploads")

# WebSocket Rooms
ws.join("chat:1", client)
ws.broadcast("chat:1", {"msg": "Hello"})
users = ws.presence("chat:1")

# AI Integration
response = await ai.chat("Summarize this", system="You are helpful")
embedding = await ai.embed("Search query")

# API Docs
docs.configure(app, title="My API", version="2.0")
```

---

## 🚀 Enterprise Features

### 1. SPA Navigation (Turbo Drive)

PyX automatically handles navigation like a Single Page Application (SPA), updating only the content that changes without full page reloads.

```python
# Automatic SPA Link
ui.link_button("Go to Dashboard", "/dashboard")

# Manual Client-Side Navigation
ui.button("Home").on_click(JS.navigate("/"))
```

### 2. Client-Side Interactions (Zero Latency)

Use `JS` helpers for instant UI updates without server roundtrips.

```python
from pyx.client import JS

# Toggle Class
ui.button("Menu").on_click(JS.toggle_class("#sidebar", "hidden"))

# Copy to Clipboard
ui.button("Share").on_click(
    JS.copy_to_clipboard("https://myapp.com").then_toast("Link copied!")
)
```

### 3. SEO Suite

Strictly typed SEO metadata generator.

```python
from pyx.seo import Metadata, JSONLD

def product_meta(params):
    return Metadata(
        title=f"Product {params.get('id')}",
        json_ld=JSONLD.product(name="iPhone", price="999")
    )

app.add_page("/product/{id}", render_page, metadata=product_meta)
```

---

## 📁 Project Structure

```
myapp/
├── main.py              # Entry point
├── pages/               # File-based routing
│   ├── index.py         # → /
│   ├── about.py         # → /about
│   └── blog/
│       └── [slug].py    # → /blog/:slug
├── models/              # Database models
├── components/          # Reusable UI
├── api/                 # API endpoints
├── tests/               # Tests
└── migrations/          # Database migrations
```

---

## 🆚 Comparison

| Feature | Flask/Django | Next.js | PyX |
|---------|:------------:|:-------:|:---:|
| Backend Python | ✅ | ❌ | ✅ |
| Frontend Python | ❌ | ❌ | ✅ |
| UI Components | ❌ | ✅ | ✅ |
| Database ORM | ✅ | ❌ | ✅ |
| Auth Built-in | ❌ | ❌ | ✅ |
| Real-time | ⚠️ | ✅ | ✅ |
| **Single Language** | ❌ | ❌ | ✅ |

---

## 📚 Documentation

| File | Description |
|------|-------------|
| [SYNTAX_GUIDE.md](SYNTAX_GUIDE.md) | UI syntax reference |
| [SYNTAX_GUIDE.md](SYNTAX_GUIDE.md) | UI syntax reference |

---

## 🔮 Roadmap

- [x] Core UI Engine (Zen Mode)
- [x] 100+ UI Components
- [x] Pythonic Styling
- [x] Database ORM with Relationships
- [x] Migrations CLI (`pyx db *`)
- [x] Authentication Module
- [x] CLI Generators
- [x] Testing Framework
- [x] Logging
- [x] Caching
- [x] i18n / PWA / SEO
- [x] Cloud Storage (S3/GCS)
- [x] WebSocket Rooms & Presence
- [x] AI/LLM Integration
- [x] OpenAPI/Swagger Docs
- [x] **State Management** ✨ NEW
- [x] **Computed Vars** (`@var` decorator) ✨ NEW
- [x] **Session Persistence** ✨ NEW
- [x] **Background Tasks** ✨ NEW
- [ ] Docker Deployment
- [ ] Cloud Templates (Vercel, Railway)

---

## 💡 Philosophy

> **"Write less, do more. Python only."**

PyX mengikuti filosofi bahwa developer productivity lebih penting dari ceremonial code. Semua bisa diakses via namespace sederhana - tidak perlu banyak import, tidak perlu context switching.

---

## 🤝 Contributing

```bash
git clone https://github.com/sukirman1901/usePyX.git
cd usePyX
pip install -e .
pyx test
```

---

*Built with ❤️ by PyX Team*
