"""
FortiOS Ethernet OAM API
Ethernet Operations, Administration and Maintenance endpoints
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....client import FortiOS


class EthernetOAM:
    """
    Ethernet OAM API helper class
    Provides access to ethernet OAM configuration endpoints
    """

    def __init__(self, client: 'FortiOS') -> None:
        """
        Initialize EthernetOAM helper

        Args:
            client: FortiOS client instance
        """
        self._client = client

        # Initialize endpoint classes
        from .cfm import Cfm

        self.cfm = Cfm(client)
