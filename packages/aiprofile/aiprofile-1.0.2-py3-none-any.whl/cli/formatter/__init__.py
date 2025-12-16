"""Formatter module for terminal output."""

from .interface import IFormatter
from .formatter import RichFormatter

__all__ = ["IFormatter", "RichFormatter"]
