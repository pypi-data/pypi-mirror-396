# Core
from .core.server import App
from .core.router import Router, Route, auto_discover_pages
from .core.state import State, StateManager, redirect, alert, toast, refresh, Action, var, computed
from .core.events import EventManager, event
from .core.tasks import background, BackgroundTask, delayed, periodic, run_async
from .core.context import router, RouterContext, PageInfo
from .core.reactive import ReactiveValue, rx, cond, foreach, match, text
from .core.env import env, Env
from .core.database import Model, Field, session, Query, configure_db, create_tables, select
from .core.session import Session, SessionStorage, SessionConfig, generate_session_id
from .core.middleware import (
    LoggingMiddleware,
    CORSMiddleware,
    RateLimitMiddleware,
    AuthMiddleware,
    ErrorHandlerMiddleware,
    CSRFMiddleware,
    protected,
    require_role,
    require_permission
)

# SSG (Static Site Generation)
from .core.ssg import StaticSiteGenerator, BuildConfig

# Web (UI & Frontend)
from .web.ui import Element, UI, ui
from .web.colors import Colors
from .web.components import PyxUI, Lucide, Chart, chart, DataGrid, datagrid
from .web.components import Draggable, DropZone, SortableList, Kanban
from .web.components import TradingChart, CandlestickChart, candlestick_chart
from .web.components.datagrid import Column as GridColumn
from .web.client import JS, ClientStorage, storage as browser_storage

# Theme & Styling
from .web.theme import Theme, Themes, theme, ThemeProvider, DarkModeToggle

# Pythonic Styles
from .web.styles import Style, style, sx, presets, ResponsiveStyle, States

# Layout Utilities
from .web.layout import Container, Stack, HStack, Center, Spacer, Divider, Grid, AspectRatio, Card

# Responsive Utilities
from .web.responsive import responsive, Show, Hide, ResponsiveStyles, BREAKPOINTS

# Animation
from .web.animation import Animate, Transition, Spinner, fade_in, slide_up, scale_in, spin, pulse, bounce

# Developer Tools
from .web.devtools import IconBrowser, ResponsivePreview, DevToolbar, LUCIDE_ICONS

# Form Validation
from .web.validation import Validators, FormValidator, ValidatedInput, ValidatedForm

# Accessibility
from .web.a11y import A11y, FocusTrap, SkipLink, VisuallyHidden, LiveRegion, KeyboardNav, A11yStyles

# Suspense & Loading States
from .web.suspense import Suspense, ErrorBoundary, Loading, suspense, error_boundary

# Edge Runtime
from .core.edge import edge, EdgeFunction, EdgeConfig, EdgeDeployer, middleware, rewrite
from .core.edge import redirect as edge_redirect  # Edge-specific redirect
from .core.edge import cache as edge_cache  # Edge cache decorator

# Plugin System
from .core.plugins import plugins, PluginManager, PluginInfo, use_plugin

# Data
from .data.database import (
    Model, Column, db, Relationship,
    PrimaryKey, ForeignKey, CreatedAt, UpdatedAt, QueryBuilder
)

# Lib (Batteries)
from .lib.auth import auth, User, Session
from .lib.audit import Audit, track_activity
from .lib.email import email, Email
from .lib.jobs import jobs, BackgroundWorker
from .lib.validation import validate, validate_or_fail, Validator, ValidationError
from .lib.seo import Head, seo, Metadata, OpenGraph, TwitterCard, JSONLD
from .lib.i18n import i18n, t, locale, Locale, LocaleMiddleware
from .lib.pwa import PWA, PWAConfig, PWAIcon, pwa_head

# =========================================================================
# ZEN MODE NAMESPACES
# =========================================================================

# Testing (test.*)
from .core.testing import test, TestClient, TestResponse, TestDatabase

# Logging (log.*)
from .core.logging import log, ZenLogger, LogLevel

# Caching (cache.*)
from .core.cache import cache, ZenCache

# File Upload
from .web.components.upload import upload, FileUpload

# Security (security.*)
from .core.security import (
    security, ZenSecurity,
    PasswordHasher, PasswordPolicy, AccountLockout,
    SecurityHeaders, escape_html, sanitize_html
)

# Storage (storage.*) - Cloud & Local
from .core.storage import storage, ZenStorage

# WebSocket Rooms (ws.*)
from .core.websocket import ws, ZenWebSocket

# AI Integration (ai.*)
from .core.ai import ai, ZenAI

# API Documentation (docs.*)
from .core.docs import docs, ZenDocs
