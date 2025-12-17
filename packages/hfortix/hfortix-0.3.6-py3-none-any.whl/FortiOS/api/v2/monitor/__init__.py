"""
FortiOS Monitor API
Real-time monitoring and status endpoints

Note: Monitor API endpoints are not yet implemented.
This is a placeholder for future development.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Union

if TYPE_CHECKING:
    from ...client import FortiOS

__all__ = ['Monitor']


class Monitor:
    """
    Monitor API helper class
    Provides access to FortiOS monitoring endpoints (Coming Soon)

    The Monitor API provides real-time status information and monitoring
    capabilities for FortiGate devices. This module is under development.

    Planned categories (0/29 implemented):
    - system/ - System status and performance
    - firewall/ - Firewall statistics and sessions
    - router/ - Routing table and statistics
    - vpn/ - VPN status and tunnels
    - user/ - User authentication status
    - wifi/ - WiFi status and clients
    - switch-controller/ - Switch management
    - log/ - Log statistics
    - webfilter/ - Web filtering statistics
    - antivirus/ - Antivirus status
    - ips/ - IPS status
    - application/ - Application control statistics
    - endpoint-control/ - Endpoint status
    - network/ - Network statistics
    - fortiguard/ - FortiGuard status
    - license/ - License information
    - system-config/ - Configuration status
    - utm/ - UTM statistics
    - And 11 more...
    """

    def __init__(self, client: 'FortiOS') -> None:
        """
        Initialize Monitor helper

        Args:
            client: FortiOS client instance
        """
        self._client = client

    def _get(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
        vdom: Optional[Union[str, bool]] = None
    ) -> dict[str, Any]:
        """
        GET request to Monitor API (Advanced/Internal)
        
        ⚠️ Advanced Usage: For endpoints without dedicated classes.

        Args:
            path: Endpoint path (e.g., 'system/status', 'firewall/session')
            params: Query parameters dict
            vdom: Virtual domain (None=use default, False=skip vdom, or specific vdom)

        Returns:
            JSON response

        Examples:
            >>> # Get system status
            >>> monitor._get('system/status')

            >>> # Get firewall sessions
            >>> monitor._get('firewall/session')

        Note:
            Most monitor endpoints are read-only (GET only) and provide
            real-time status information.
        """
        return self._client.get('monitor', path, params=params, vdom=vdom)
