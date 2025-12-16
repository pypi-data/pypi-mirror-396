
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


class PrivacyValueDisallowChatParticipants(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.PrivacyRule`.

    Details:
        - Layer: ``166``
        - ID: ``41C87565``

    Parameters:
        chats (List of ``int`` ``64-bit``):
            N/A

    """

    __slots__: List[str] = ["chats"]

    ID = 0x41c87565
    QUALNAME = "types.PrivacyValueDisallowChatParticipants"

    def __init__(self, *, chats: List[int]) -> None:
        self.chats = chats  # Vector<long>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PrivacyValueDisallowChatParticipants":
        # No flags
        
        chats = TLObject.read(b, Long)
        
        return PrivacyValueDisallowChatParticipants(chats=chats)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.chats, Long))
        
        return b.getvalue()
