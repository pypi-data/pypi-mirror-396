
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


class MessageActionChannelCreate(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.MessageAction`.

    Details:
        - Layer: ``166``
        - ID: ``95D2AC92``

    Parameters:
        title (``str``):
            N/A

    """

    __slots__: List[str] = ["title"]

    ID = 0x95d2ac92
    QUALNAME = "types.MessageActionChannelCreate"

    def __init__(self, *, title: str) -> None:
        self.title = title  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageActionChannelCreate":
        # No flags
        
        title = String.read(b)
        
        return MessageActionChannelCreate(title=title)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.title))
        
        return b.getvalue()
