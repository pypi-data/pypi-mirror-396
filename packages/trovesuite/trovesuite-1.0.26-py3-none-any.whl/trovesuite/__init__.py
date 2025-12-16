"""
TroveSuite Package

A comprehensive authentication, authorization, notification, and storage service for ERP systems.
Provides JWT token validation, user authorization, permission checking, notification capabilities,
Azure Storage blob management, and utility functions for multi-tenant applications.
"""

from .auth import AuthService
from .notification import NotificationService
from .storage import StorageService
from .utils import Helper

__version__ = "1.0.20"
__author__ = "Bright Debrah Owusu"
__email__ = "owusu.debrah@deladetech.com"

__all__ = [
    "AuthService",
    "NotificationService",
    "StorageService",
    "Helper",
]
