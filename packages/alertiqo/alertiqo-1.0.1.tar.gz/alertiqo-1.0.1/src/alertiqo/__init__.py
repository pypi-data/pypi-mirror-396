"""Alertiqo Python SDK for error tracking."""

from .client import Alertiqo
from .middleware import alertiqo_middleware

__version__ = "1.0.0"
__all__ = ["Alertiqo", "alertiqo_middleware"]
