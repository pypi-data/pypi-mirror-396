
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


class GetPeerDialogs(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``166``
        - ID: ``E470BCFD``

    Parameters:
        peers (List of :obj:`InputDialogPeer <zeebgram.raw.base.InputDialogPeer>`):
            N/A

    Returns:
        :obj:`messages.PeerDialogs <zeebgram.raw.base.messages.PeerDialogs>`
    """

    __slots__: List[str] = ["peers"]

    ID = 0xe470bcfd
    QUALNAME = "functions.messages.GetPeerDialogs"

    def __init__(self, *, peers: List["raw.base.InputDialogPeer"]) -> None:
        self.peers = peers  # Vector<InputDialogPeer>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetPeerDialogs":
        # No flags
        
        peers = TLObject.read(b)
        
        return GetPeerDialogs(peers=peers)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.peers))
        
        return b.getvalue()
