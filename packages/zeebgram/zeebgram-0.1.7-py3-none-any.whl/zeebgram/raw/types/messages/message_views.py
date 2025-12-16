
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


class MessageViews(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.messages.MessageViews`.

    Details:
        - Layer: ``166``
        - ID: ``B6C4F543``

    Parameters:
        views (List of :obj:`MessageViews <zeebgram.raw.base.MessageViews>`):
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

            messages.GetMessagesViews
    """

    __slots__: List[str] = ["views", "chats", "users"]

    ID = 0xb6c4f543
    QUALNAME = "types.messages.MessageViews"

    def __init__(self, *, views: List["raw.base.MessageViews"], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.views = views  # Vector<MessageViews>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageViews":
        # No flags
        
        views = TLObject.read(b)
        
        chats = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return MessageViews(views=views, chats=chats, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.views))
        
        b.write(Vector(self.chats))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
