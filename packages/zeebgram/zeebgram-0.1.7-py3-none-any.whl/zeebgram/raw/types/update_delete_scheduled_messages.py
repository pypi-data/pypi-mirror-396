
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


class UpdateDeleteScheduledMessages(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.Update`.

    Details:
        - Layer: ``166``
        - ID: ``90866CEE``

    Parameters:
        peer (:obj:`Peer <zeebgram.raw.base.Peer>`):
            N/A

        messages (List of ``int`` ``32-bit``):
            N/A

    """

    __slots__: List[str] = ["peer", "messages"]

    ID = 0x90866cee
    QUALNAME = "types.UpdateDeleteScheduledMessages"

    def __init__(self, *, peer: "raw.base.Peer", messages: List[int]) -> None:
        self.peer = peer  # Peer
        self.messages = messages  # Vector<int>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateDeleteScheduledMessages":
        # No flags
        
        peer = TLObject.read(b)
        
        messages = TLObject.read(b, Int)
        
        return UpdateDeleteScheduledMessages(peer=peer, messages=messages)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.peer.write())
        
        b.write(Vector(self.messages, Int))
        
        return b.getvalue()
