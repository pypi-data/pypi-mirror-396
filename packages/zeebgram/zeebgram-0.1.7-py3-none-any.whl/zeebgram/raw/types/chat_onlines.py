
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


class ChatOnlines(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.ChatOnlines`.

    Details:
        - Layer: ``166``
        - ID: ``F041E250``

    Parameters:
        onlines (``int`` ``32-bit``):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: zeebgram.raw.functions

        .. autosummary::
            :nosignatures:

            messages.GetOnlines
    """

    __slots__: List[str] = ["onlines"]

    ID = 0xf041e250
    QUALNAME = "types.ChatOnlines"

    def __init__(self, *, onlines: int) -> None:
        self.onlines = onlines  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChatOnlines":
        # No flags
        
        onlines = Int.read(b)
        
        return ChatOnlines(onlines=onlines)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.onlines))
        
        return b.getvalue()
