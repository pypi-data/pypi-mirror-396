"""
Mixins for AWS Lambda handlers.

This package provides mixins for common Lambda handler patterns:
- WebHandler: Activity tracking, logging, and error handling
- DataServiceMixin: Generic CRUD operations for database-backed APIs
"""

from .web_handler import WebHandler
from .data_service import DataServiceMixin

__all__ = ['WebHandler', 'DataServiceMixin']
