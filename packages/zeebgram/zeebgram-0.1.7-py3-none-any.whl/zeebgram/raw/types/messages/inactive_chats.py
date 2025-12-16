
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


class InactiveChats(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.messages.InactiveChats`.

    Details:
        - Layer: ``166``
        - ID: ``A927FEC5``

    Parameters:
        dates (List of ``int`` ``32-bit``):
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

            channels.GetInactiveChannels
    """

    __slots__: List[str] = ["dates", "chats", "users"]

    ID = 0xa927fec5
    QUALNAME = "types.messages.InactiveChats"

    def __init__(self, *, dates: List[int], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.dates = dates  # Vector<int>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InactiveChats":
        # No flags
        
        dates = TLObject.read(b, Int)
        
        chats = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return InactiveChats(dates=dates, chats=chats, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.dates, Int))
        
        b.write(Vector(self.chats))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
