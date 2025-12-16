
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


class ChannelParticipant(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.channels.ChannelParticipant`.

    Details:
        - Layer: ``166``
        - ID: ``DFB80317``

    Parameters:
        participant (:obj:`ChannelParticipant <zeebgram.raw.base.ChannelParticipant>`):
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

            channels.GetParticipant
    """

    __slots__: List[str] = ["participant", "chats", "users"]

    ID = 0xdfb80317
    QUALNAME = "types.channels.ChannelParticipant"

    def __init__(self, *, participant: "raw.base.ChannelParticipant", chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.participant = participant  # ChannelParticipant
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChannelParticipant":
        # No flags
        
        participant = TLObject.read(b)
        
        chats = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return ChannelParticipant(participant=participant, chats=chats, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.participant.write())
        
        b.write(Vector(self.chats))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
