"""
FortiOS Email Filter API
Email filtering configuration endpoints
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....client import FortiOS


class EmailFilter:
    """
    Email Filter API helper class
    Provides access to email filtering configuration endpoints
    """

    def __init__(self, client: 'FortiOS') -> None:
        """
        Initialize EmailFilter helper

        Args:
            client: FortiOS client instance
        """
        self._client = client

        # Initialize endpoint classes
        from .block_allow_list import BlockAllowList
        from .bword import Bword
        from .dnsbl import Dnsbl
        from .fortishield import Fortishield
        from .iptrust import Iptrust
        from .mheader import Mheader
        from .options import Options
        from .profile import Profile

        self.block_allow_list = BlockAllowList(client)
        self.bword = Bword(client)
        self.dnsbl = Dnsbl(client)
        self.fortishield = Fortishield(client)
        self.iptrust = Iptrust(client)
        self.mheader = Mheader(client)
        self.options = Options(client)
        self.profile = Profile(client)
