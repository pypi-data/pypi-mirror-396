"""
FortiOS CMDB - File Filter

File filter configuration for content inspection.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....client import FortiOS

from .profile import Profile


class FileFilter:
    """
    File Filter helper class
    
    Provides access to file filter configuration endpoints.
    """

    def __init__(self, client: 'FortiOS') -> None:
        """
        Initialize File Filter helper

        Args:
            client: FortiOS client instance
        """
        self._client = client
        
        # Initialize endpoint classes
        self.profile = Profile(client)
