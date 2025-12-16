
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


class SendVote(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``166``
        - ID: ``10EA6184``

    Parameters:
        peer (:obj:`InputPeer <zeebgram.raw.base.InputPeer>`):
            N/A

        msg_id (``int`` ``32-bit``):
            N/A

        options (List of ``bytes``):
            N/A

    Returns:
        :obj:`Updates <zeebgram.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "msg_id", "options"]

    ID = 0x10ea6184
    QUALNAME = "functions.messages.SendVote"

    def __init__(self, *, peer: "raw.base.InputPeer", msg_id: int, options: List[bytes]) -> None:
        self.peer = peer  # InputPeer
        self.msg_id = msg_id  # int
        self.options = options  # Vector<bytes>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SendVote":
        # No flags
        
        peer = TLObject.read(b)
        
        msg_id = Int.read(b)
        
        options = TLObject.read(b, Bytes)
        
        return SendVote(peer=peer, msg_id=msg_id, options=options)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.peer.write())
        
        b.write(Int(self.msg_id))
        
        b.write(Vector(self.options, Bytes))
        
        return b.getvalue()
