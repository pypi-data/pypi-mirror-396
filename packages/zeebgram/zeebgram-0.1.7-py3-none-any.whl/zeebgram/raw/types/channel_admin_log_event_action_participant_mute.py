
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


class ChannelAdminLogEventActionParticipantMute(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``166``
        - ID: ``F92424D2``

    Parameters:
        participant (:obj:`GroupCallParticipant <zeebgram.raw.base.GroupCallParticipant>`):
            N/A

    """

    __slots__: List[str] = ["participant"]

    ID = 0xf92424d2
    QUALNAME = "types.ChannelAdminLogEventActionParticipantMute"

    def __init__(self, *, participant: "raw.base.GroupCallParticipant") -> None:
        self.participant = participant  # GroupCallParticipant

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChannelAdminLogEventActionParticipantMute":
        # No flags
        
        participant = TLObject.read(b)
        
        return ChannelAdminLogEventActionParticipantMute(participant=participant)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.participant.write())
        
        return b.getvalue()
