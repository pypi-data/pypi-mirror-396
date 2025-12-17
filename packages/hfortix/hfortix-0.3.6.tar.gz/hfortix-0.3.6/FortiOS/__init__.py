"""
FortiOS Python SDK

Python client for interacting with Fortinet FortiGate firewalls via REST API.
Supports configuration management (CMDB), monitoring, logging, and services.

Main Classes:
    FortiOS: Main API client class
    
API Categories:
    - cmdb: Configuration Management Database
    - monitor: Real-time monitoring and status
    - log: Log queries and analysis
    - service: System services

Exceptions:
    FortiOSError: Base exception for FortiOS-specific errors
    LoginError: Authentication failure
    APIError: API request/response errors
"""

from .client import FortiOS
from .exceptions import APIError, FortiOSError, LoginError
from .version import __author__, __version__

__all__ = [
    # Main client
    'FortiOS',
    
    # Exceptions
    'FortiOSError',
    'LoginError', 
    'APIError',
    
    # Version info
    '__version__',
    '__author__',
]
