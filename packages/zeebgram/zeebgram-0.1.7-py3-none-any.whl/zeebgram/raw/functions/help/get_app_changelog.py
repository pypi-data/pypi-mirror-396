
from io import BytesIO

from zeebgram.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from zeebgram.raw.core import TLObject
from zeebgram import raw
from typing import List, Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class GetAppChangelog(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``166``
        - ID: ``9010EF6F``

    Parameters:
        prev_app_version (``str``):
            N/A

    Returns:
        :obj:`Updates <zeebgram.raw.base.Updates>`
    """

    __slots__: List[str] = ["prev_app_version"]

    ID = 0x9010ef6f
    QUALNAME = "functions.help.GetAppChangelog"

    def __init__(self, *, prev_app_version: str) -> None:
        self.prev_app_version = prev_app_version  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetAppChangelog":
        # No flags
        
        prev_app_version = String.read(b)
        
        return GetAppChangelog(prev_app_version=prev_app_version)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.prev_app_version))
        
        return b.getvalue()
