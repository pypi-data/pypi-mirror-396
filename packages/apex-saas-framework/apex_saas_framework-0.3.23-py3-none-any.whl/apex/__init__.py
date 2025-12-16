"""
Apex - Pure Python Library for SaaS Functionality

Organized imports by functionality:

# Core Setup
from apex import Client, set_default_client, bootstrap

# Authentication
from apex.auth import signup, login, verify_token, refresh_token, forgot_password, reset_password, change_password

# Users
from apex.users import create_user, get_user, update_user, delete_user

# Email (SendGrid)
from apex.email import send_email, send_bulk_email, sendgrid

# Migrations
from apex.migrations import setup_alembic, get_sync_url, find_models

# Database Utilities
from apex.database import get_sync_url, get_async_url

# Models (Simple names!)
from apex.models import Model, ID, Timestamps, register_model, create_tables
"""

__version__ = "0.3.23"

# ============================================
# CORE SETUP
# ============================================
from apex.client import Client
from apex.sync import set_default_client, bootstrap

# ============================================
# AUTHENTICATION (Re-export from apex.auth)
# ============================================
from apex.auth import (
    signup,
    login,
    verify_token,
    refresh_token as refresh_access_token,
    forgot_password,
    reset_password,
    change_password,
)

# ============================================
# USERS (Re-export from apex.users)
# ============================================
from apex.users import create_user, get_user, update_user, delete_user

# ============================================
# EMAIL (Re-export from apex.email)
# ============================================
from apex.email import send_email, send_bulk_email, sendgrid

# ============================================
# ORGANIZATIONS (Re-export from apex.organizations)
# ============================================
from apex.organizations import create_organization, get_organization, list_organizations

# ============================================
# MIGRATIONS (Re-export from apex.migrations)
# ============================================
from apex.migrations import (
    setup_alembic,
    get_sync_url as migrations_get_sync_url,
    find_models,
    validate_database_url,
    sanitize_database_url,
    mask_sensitive_url,
)

# ============================================
# DATABASE (Re-export from apex.database)
# ============================================
from apex.database import get_sync_url, get_async_url

# ============================================
# MODELS (Simple, intuitive names!)
# ============================================
from apex.models import (
    # Simple names (recommended)
    Model,
    ID,
    IntID,
    StrID,
    Timestamps,
    CreatedUpdated,
    AutoTimestamps,
    # Registry
    register_model,
    create_tables,
    # Technical names (for advanced users)
    Base,
    UUIDPKMixin,
    TimestampMixin,
    IntegerPKMixin,
    StringPKMixin,
    MySQLUUIDMixin,
    FlexibleBaseModel,
    JSONType,
    # Pre-defined models
    User,
    Organization,
    OrganizationLocation,
    Role,
    Permission,
    BaseUser,
    BaseOrganization,
    BaseOrganizationLocation,
    BaseRole,
    BasePermission,
    # Helpers
    define_model,
    get_registry,
    validate_models,
    get_all_models,
    auto_table_name,
)

# ============================================
# ADVANCED (Resources - Optional)
# ============================================
from apex.resources.users import Users
from apex.resources.auth import Auth
from apex.resources.organizations import Organizations
from apex.resources.roles import Roles
from apex.resources.permissions import Permissions
from apex.resources.modules import Modules
from apex.resources.settings import Settings
from apex.resources.payments import Payments
from apex.resources.email import Email
from apex.resources.files import Files

# Sync convenience wrappers (optional)
from apex import sync as sync_api

# ============================================
# QUICK START (Reduce code writing)
# ============================================
from apex.quickstart import (
    quick_setup,
    quick_model,
    quick_user,
    auto_setup,
)
from apex.setup import setup

# ============================================
# CONFIGURATION
# ============================================
from apex.core.config import Settings, get_settings

__all__ = [
    # Core Setup
    "Client",
    "set_default_client",
    "bootstrap",
    
    # Authentication
    "signup",
    "login",
    "verify_token",
    "refresh_access_token",
    "forgot_password",
    "reset_password",
    "change_password",
    
    # Users
    "create_user",
    "get_user",
    "update_user",
    "delete_user",
    
    # Organizations
    "create_organization",
    "get_organization",
    "list_organizations",
    
    # Email
    "send_email",
    "send_bulk_email",
    "sendgrid",
    
    # Migrations
    "setup_alembic",
    "migrations_get_sync_url",
    "find_models",
    "validate_database_url",
    "sanitize_database_url",
    "mask_sensitive_url",
    
    # Database
    "get_sync_url",
    "get_async_url",
    
    # Models - Simple names (recommended)
    "Model",
    "ID",
    "IntID",
    "StrID",
    "Timestamps",
    "CreatedUpdated",
    "AutoTimestamps",
    "register_model",
    "create_tables",
    
    # Models - Technical names (advanced)
    "Base",
    "UUIDPKMixin",
    "TimestampMixin",
    "IntegerPKMixin",
    "StringPKMixin",
    "MySQLUUIDMixin",
    "FlexibleBaseModel",
    "JSONType",
    
    # Models - Pre-defined
    "User",
    "Organization",
    "OrganizationLocation",
    "Role",
    "Permission",
    "BaseUser",
    "BaseOrganization",
    "BaseOrganizationLocation",
    "BaseRole",
    "BasePermission",
    
    # Models - Helpers
    "define_model",
    "get_registry",
    "validate_models",
    "get_all_models",
    "auto_table_name",
    
    # Advanced Resources
    "Users",
    "Auth",
    "Organizations",
    "Roles",
    "Permissions",
    "Modules",
    "Settings",
    "Payments",
    "Email",
    "Files",
    
    # Sync wrappers (optional)
    "sync_api",
    
    # Quick Start (Reduce code writing)
    "quick_setup",
    "quick_model",
    "quick_user",
    "auto_setup",
    "setup",  # Simplest - just setup()
    
    # Configuration
    "get_settings",
    
    # Version
    "__version__",
]

