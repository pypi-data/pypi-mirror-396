
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


class AdminLogResults(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.channels.AdminLogResults`.

    Details:
        - Layer: ``166``
        - ID: ``ED8AF74D``

    Parameters:
        events (List of :obj:`ChannelAdminLogEvent <zeebgram.raw.base.ChannelAdminLogEvent>`):
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

            channels.GetAdminLog
    """

    __slots__: List[str] = ["events", "chats", "users"]

    ID = 0xed8af74d
    QUALNAME = "types.channels.AdminLogResults"

    def __init__(self, *, events: List["raw.base.ChannelAdminLogEvent"], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.events = events  # Vector<ChannelAdminLogEvent>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "AdminLogResults":
        # No flags
        
        events = TLObject.read(b)
        
        chats = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return AdminLogResults(events=events, chats=chats, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.events))
        
        b.write(Vector(self.chats))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
