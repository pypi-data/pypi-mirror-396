"""Polarion MCP Server - Model Context Protocol integration for Siemens Polarion ALM."""

__version__ = "0.1.0"
__author__ = "ATOMS Team"

from .client import PolarionClient

__all__ = ["PolarionClient", "__version__"]
