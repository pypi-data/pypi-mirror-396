
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


class PeerSettings(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.messages.PeerSettings`.

    Details:
        - Layer: ``166``
        - ID: ``6880B94D``

    Parameters:
        settings (:obj:`PeerSettings <zeebgram.raw.base.PeerSettings>`):
            N/A

        chats (List of :obj:`Chat <zeebgram.raw.base.Chat>`):
            N/A

        users (List of :obj:`User <zeebgram.raw.base.User>`):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: zeebgram.raw.functions

        .. autosummary::
            :nosignatures:

            messages.GetPeerSettings
    """

    __slots__: List[str] = ["settings", "chats", "users"]

    ID = 0x6880b94d
    QUALNAME = "types.messages.PeerSettings"

    def __init__(self, *, settings: "raw.base.PeerSettings", chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.settings = settings  # PeerSettings
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PeerSettings":
        # No flags
        
        settings = TLObject.read(b)
        
        chats = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return PeerSettings(settings=settings, chats=chats, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.settings.write())
        
        b.write(Vector(self.chats))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
