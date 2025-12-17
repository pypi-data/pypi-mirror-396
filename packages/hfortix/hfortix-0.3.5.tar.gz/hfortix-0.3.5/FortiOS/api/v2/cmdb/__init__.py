"""
FortiOS CMDB API
Configuration Management Database endpoints
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Union

if TYPE_CHECKING:
    from ...client import FortiOS


class CMDB:
    """
    CMDB API helper class
    Provides access to FortiOS configuration endpoints
    
    Attributes:
        alertemail: Alert email configuration
        antivirus: Antivirus profiles and settings
        application: Application control lists
        authentication: Authentication rules and settings
        automation: Automation stitches and actions
        casb: Cloud Access Security Broker
        certificate: Certificate management
        diameter_filter: Diameter filter profiles
        dlp: Data Loss Prevention
        dnsfilter: DNS filtering profiles
        emailfilter: Email filter profiles
        endpoint_control: Endpoint control settings
        ethernet_oam: Ethernet OAM settings
        extension_controller: Extension controller
        file_filter: File filtering profiles
        firewall: Firewall policies and objects
    """

    def __init__(self, client: 'FortiOS') -> None:
        """
        Initialize CMDB helper

        Args:
            client: FortiOS client instance
        """
        self._client = client

        # Initialize endpoint classes
        from .alertemail import AlertEmail
        from .antivirus import Antivirus
        from .application import Application
        from .authentication import Authentication
        from .automation import Automation
        from .casb import Casb
        from .certificate import Certificate
        from .diameter_filter import DiameterFilter
        from .dlp import DLP
        from .dnsfilter import DNSFilter
        from .emailfilter import EmailFilter
        from .endpoint_control import EndpointControl
        from .ethernet_oam import EthernetOAM
        from .extension_controller import ExtensionController
        from .file_filter import FileFilter
        from .firewall import Firewall

        self.alertemail: AlertEmail = AlertEmail(client)
        self.antivirus: Antivirus = Antivirus(client)
        self.application: Application = Application(client)
        self.authentication: Authentication = Authentication(client)
        self.automation: Automation = Automation(client)
        self.casb: Casb = Casb(client)
        self.certificate: Certificate = Certificate(client)
        self.diameter_filter: DiameterFilter = DiameterFilter(client)
        self.dlp: DLP = DLP(client)
        self.dnsfilter: DNSFilter = DNSFilter(client)
        self.emailfilter: EmailFilter = EmailFilter(client)
        self.endpoint_control: EndpointControl = EndpointControl(client)
        self.ethernet_oam: EthernetOAM = EthernetOAM(client)
        self.extension_controller: ExtensionController = ExtensionController(client)
        self.file_filter: FileFilter = FileFilter(client)
        self.firewall: Firewall = Firewall(client)

    def get(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
        vdom: Optional[Union[str, bool]] = None
    ) -> dict[str, Any]:
        """
        GET request to CMDB API

        Args:
            path: Endpoint path (e.g., 'firewall/address', 'alertemail/setting')
            params: Query parameters dict
            vdom: Virtual domain (None=use default, False=skip vdom, or specific vdom)

        Returns:
            JSON response

        Examples:
            # Get all firewall addresses
            cmdb.get('firewall/address')

            # Get specific address
            cmdb.get('firewall/address/myaddr')

            # With filters
            cmdb.get('firewall/address', params={'format': 'name|comment'})

            # Skip vdom
            cmdb.get('alertemail/setting', vdom=False)
        """
        return self._client.request('GET', 'cmdb', path, params=params, vdom=vdom)

    def post(
        self,
        path: str,
        data: dict[str, Any],
        params: Optional[dict[str, Any]] = None,
        vdom: Optional[Union[str, bool]] = None
    ) -> dict[str, Any]:
        """
        POST request to CMDB API - Create new object

        Args:
            path: Endpoint path
            data: Object data to create
            params: Query parameters (action=clone, nkey, etc.)
            vdom: Virtual domain

        Returns:
            JSON response

        Examples:
            # Create firewall address (using RFC 5737 example network)
            cmdb.post('firewall/address', {'name': 'test', 'subnet': '192.0.2.0/24'})

            # Clone existing
            cmdb.post('firewall/address', data, params={'action': 'clone', 'nkey': 'new_name'})
        """
        return self._client.request('POST', 'cmdb', path, data=data, params=params, vdom=vdom)

    def put(
        self,
        path: str,
        data: dict[str, Any],
        params: Optional[dict[str, Any]] = None,
        vdom: Optional[Union[str, bool]] = None
    ) -> dict[str, Any]:
        """
        PUT request to CMDB API - Update existing object

        Args:
            path: Endpoint path (include object identifier)
            data: Updated object data
            params: Query parameters (action=move, before, after, etc.)
            vdom: Virtual domain

        Returns:
            JSON response

        Examples:
            # Update firewall address (using RFC 5737 example network)
            cmdb.put('firewall/address/myaddr', {'subnet': '198.51.100.0/24'})

            # Move object
            cmdb.put('firewall/policy/1', data, params={'action': 'move', 'after': '5'})
        """
        return self._client.request('PUT', 'cmdb', path, data=data, params=params, vdom=vdom)

    def delete(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
        vdom: Optional[Union[str, bool]] = None
    ) -> dict[str, Any]:
        """
        DELETE request to CMDB API - Delete object

        Args:
            path: Endpoint path (include object identifier)
            params: Query parameters
            vdom: Virtual domain

        Returns:
            JSON response

        Examples:
            # Delete firewall address
            cmdb.delete('firewall/address/myaddr')
        """
        return self._client.request('DELETE', 'cmdb', path, params=params, vdom=vdom)
