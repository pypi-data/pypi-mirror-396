
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


class GetAttachMenuBots(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``166``
        - ID: ``16FCC2CB``

    Parameters:
        hash (``int`` ``64-bit``):
            N/A

    Returns:
        :obj:`AttachMenuBots <zeebgram.raw.base.AttachMenuBots>`
    """

    __slots__: List[str] = ["hash"]

    ID = 0x16fcc2cb
    QUALNAME = "functions.messages.GetAttachMenuBots"

    def __init__(self, *, hash: int) -> None:
        self.hash = hash  # long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetAttachMenuBots":
        # No flags
        
        hash = Long.read(b)
        
        return GetAttachMenuBots(hash=hash)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.hash))
        
        return b.getvalue()
