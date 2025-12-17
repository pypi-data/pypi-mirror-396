from __future__ import annotations

from typing import Any, Optional, Union

import requests


class FortiOS:
    """
    FortiOS REST API Client
    
    Python client for interacting with Fortinet FortiGate firewalls via REST API.
    Supports configuration management (CMDB), monitoring, logging, and services.
    
    This client uses token-based authentication and provides a stateless interface
    to FortiOS devices. No login/logout required - just initialize with your token
    and start making API calls.
    
    Main API categories:
        - cmdb: Configuration Management Database (firewall policies, objects, etc.)
        - monitor: Real-time monitoring and status
        - log: Log queries and analysis
        - service: System services (sniffer, security rating, etc.)
    
    Attributes:
        host (str): FortiGate hostname or IP address
        url (str): Complete HTTPS URL to FortiGate
        verify (bool): SSL certificate verification enabled/disabled
        vdom (str): Active virtual domain (None = default VDOM)
        port (int): HTTPS port number
        session (requests.Session): HTTP session with connection pooling
        cmdb (CMDB): Configuration management interface
        monitor (Monitor): Monitoring interface
        log (Log): Logging interface
        service (Service): Services interface
    
    Example:
        >>> from fortinet import FortiOS
        >>> fgt = FortiOS("fortigate.example.com", token="your_token_here")
        >>> 
        >>> # List firewall addresses
        >>> addresses = fgt.cmdb.firewall.address.list()
        >>> 
        >>> # Create a firewall address
        >>> fgt.cmdb.firewall.address.create(
        ...     name='test-host',
        ...     subnet='192.0.2.100/32',
        ...     comment='Example host'
        ... )
        >>> 
        >>> # Get system status
        >>> status = fgt.monitor.system.status.get()
    
    Note:
        - Requires FortiOS 6.0+ with REST API enabled
        - API token must be created in FortiOS: System > Admin > API Users
        - Use verify=False only in development with self-signed certificates
    
    See Also:
        - API Reference: https://docs.fortinet.com/
        - Token Setup: QUICKSTART.md
        - Examples: EXAMPLES.md
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        token: Optional[str] = None,
        verify: bool = True,
        vdom: Optional[str] = None,
        port: Optional[int] = None
    ) -> None:
        """
        Initialize FortiOS API client

        With token authentication, everything is stateless - just provide credentials
        and start making API calls. No login/logout needed.

        Args:
            host: FortiGate IP/hostname (e.g., "192.0.2.10" or "fortigate.example.com")
            token: API token for authentication
            verify: Verify SSL certificates (default: True, recommended for production)
            vdom: Virtual domain (default: None = FortiGate's default VDOM)
            port: HTTPS port (default: None = use 443, or specify custom port like 8443)

        Examples:
            # Production - with valid SSL certificate
            fgt = FortiOS("fortigate.example.com", token="your_token_here", verify=True)

            # Development/Testing - with self-signed certificate (example IP from RFC 5737)
            fgt = FortiOS("192.0.2.10", token="your_token_here", verify=False)

            # Custom port
            fgt = FortiOS("192.0.2.10", token="your_token_here", verify=False, port=8443)

            # Port in hostname (alternative)
            fgt = FortiOS("192.0.2.10:8443", token="your_token_here", verify=False)
        """
        self.host = host
        self.vdom = vdom
        self.port = port

        # Build URL with port handling
        if host:
            # If port is already in host string, use as-is
            if ':' in host:
                self.url = f"https://{host}"
            # If explicit port provided, append it
            elif port:
                self.url = f"https://{host}:{port}"
            # Otherwise use default (443)
            else:
                self.url = f"https://{host}"
        else:
            self.url = None

        self.verify = verify
        self.session = requests.Session()
        self.session.verify = verify

        if not verify:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Set token if provided
        if token:
            self.session.headers['Authorization'] = f'Bearer {token}'

        # Initialize API helpers
        from .api.v2.cmdb import CMDB
        from .api.v2.log import Log
        from .api.v2.monitor import Monitor
        from .api.v2.service import Service
        
        self.cmdb: CMDB = CMDB(self)
        self.service: Service = Service(self)
        self.log: Log = Log(self)
        self.monitor: Monitor = Monitor(self)

    def _handle_response_errors(self, response: requests.Response) -> None:
        """
        Handle HTTP response errors consistently

        Args:
            response: requests.Response object

        Raises:
            APIError: If response contains JSON error details
            HTTPError: If response is not JSON (via raise_for_status)
        """
        if not response.ok:
            try:
                error_detail = response.json()
                from .exceptions import APIError
                raise APIError(
                    f"HTTP {response.status_code}: {error_detail}"
                )
            except ValueError:
                # If response is not JSON, raise standard HTTP error
                response.raise_for_status()

    def request(
        self,
        method: str,
        api_type: str,
        path: str,
        data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        vdom: Optional[Union[str, bool]] = None
    ) -> dict[str, Any]:
        """
        Generic request method for all API calls

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            api_type: API type (cmdb, monitor, log, service)
            path: API endpoint path (e.g., 'firewall/address', 'system/status')
            data: Request body data (for POST/PUT)
            params: Query parameters dict
            vdom: Virtual domain (None=use default, or specify vdom name)

        Returns:
            JSON response
        """
        url = f"{self.url}/api/v2/{api_type}/{path}"
        params = params or {}

        # Only add vdom parameter if explicitly specified (either from login or this call)
        # Following Fortinet documentation: vdom parameter is optional
        if vdom is not None:
            # Use specific vdom for this request
            params['vdom'] = vdom
        elif self.vdom is not None and 'vdom' not in params:
            # Use default vdom from login
            params['vdom'] = self.vdom
        # else: No vdom parameter (FortiGate uses its default)

        # Make request
        res = self.session.request(
            method=method,
            url=url,
            json=data if data else None,
            params=params if params else None
        )

        # Handle errors
        self._handle_response_errors(res)

        return res.json()

    def get(
        self,
        api_type: str,
        path: str,
        params: Optional[dict[str, Any]] = None,
        vdom: Optional[Union[str, bool]] = None
    ) -> dict[str, Any]:
        """
        GET request

        Args:
            api_type: cmdb, monitor, log, service
            path: Endpoint path (e.g., 'firewall/address', 'firewall/address/myaddr')
            params: Query parameters (format, filter, mkey, etc.)
            vdom: Virtual domain (None=use default, False=skip vdom, or specific vdom)

        Examples:
            # Get all firewall addresses
            get('cmdb', 'firewall/address')

            # Get specific address
            get('cmdb', 'firewall/address/myaddr')

            # With filters
            get('cmdb', 'firewall/address', params={'format': 'name|comment'})

            # Skip vdom
            get('cmdb', 'system/alertemail', vdom=False)

            # Monitor endpoint
            get('monitor', 'system/status', vdom=False)
        """
        return self.request('GET', api_type, path, params=params, vdom=vdom)

    def get_binary(
        self,
        api_type: str,
        path: str,
        params: Optional[dict[str, Any]] = None,
        vdom: Optional[Union[str, bool]] = None
    ) -> bytes:
        """
        GET request returning binary data (for file downloads)

        Args:
            api_type: cmdb, monitor, log, service
            path: Endpoint path
            params: Query parameters
            vdom: Virtual domain

        Returns:
            bytes: Raw binary response data

        Examples:
            # Download packet capture
            pcap_data = get_binary('service', 'sniffer/download', params={'mkey': 'any_root'})

            # Download archived file
            archive = get_binary('log', 'disk/ips/archive-download', params={'mkey': 123})
        """
        # Build URL
        url = f"{self.url}/api/v2/{api_type}/{path}"
        params = params or {}

        # Add vdom if applicable
        if vdom is not None:
            params['vdom'] = vdom
        elif self.vdom is not None and 'vdom' not in params:
            params['vdom'] = self.vdom

        # Make request
        res = self.session.get(url, params=params if params else None)

        # Handle errors
        self._handle_response_errors(res)

        # Return raw binary content
        return res.content

    def post(
        self,
        api_type: str,
        path: str,
        data: dict[str, Any],
        params: Optional[dict[str, Any]] = None,
        vdom: Optional[Union[str, bool]] = None
    ) -> dict[str, Any]:
        """
        POST request - Create new object

        Args:
            api_type: cmdb, monitor, log, service
            path: Endpoint path
            data: Object data to create
            params: Query parameters (action=clone, nkey, etc.)
            vdom: Virtual domain

        Examples:
            # Create firewall address (using RFC 5737 example network)
            post('cmdb', 'firewall/address', {'name': 'test', 'subnet': '192.0.2.0/24'})

            # Clone existing object
            post('cmdb', 'firewall/address', data, params={'action': 'clone', 'nkey': 'new_name'})
        """
        return self.request('POST', api_type, path, data=data, params=params, vdom=vdom)

    def put(
        self,
        api_type: str,
        path: str,
        data: dict[str, Any],
        params: Optional[dict[str, Any]] = None,
        vdom: Optional[Union[str, bool]] = None
    ) -> dict[str, Any]:
        """
        PUT request - Update existing object

        Args:
            api_type: cmdb, monitor, log, service
            path: Endpoint path (include object identifier)
            data: Updated object data
            params: Query parameters (action=move, before, after, etc.)
            vdom: Virtual domain

        Examples:
            # Update firewall address (using RFC 5737 example network)
            put('cmdb', 'firewall/address/myaddr', {'subnet': '198.51.100.0/24'})

            # Move object
            put('cmdb', 'firewall/policy/1', data, params={'action': 'move', 'after': '5'})
        """
        return self.request('PUT', api_type, path, data=data, params=params, vdom=vdom)

    def delete(
        self,
        api_type: str,
        path: str,
        params: Optional[dict[str, Any]] = None,
        vdom: Optional[Union[str, bool]] = None
    ) -> dict[str, Any]:
        """
        DELETE request - Delete object

        Args:
            api_type: cmdb, monitor, log, service
            path: Endpoint path (include object identifier)
            params: Query parameters
            vdom: Virtual domain

        Examples:
            # Delete firewall address
            delete('cmdb', 'firewall/address/myaddr')
        """
        return self.request('DELETE', api_type, path, params=params, vdom=vdom)

    def close(self) -> None:
        """
        Close the HTTP session and release resources

        Optional: Python automatically cleans up when object is destroyed.
        Use this for explicit resource management or in long-running apps.
        """
        if self.session:
            self.session.close()

    def __enter__(self) -> 'FortiOS':
        """Context manager entry"""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Context manager exit - automatically closes session"""
        self.close()
        return False

