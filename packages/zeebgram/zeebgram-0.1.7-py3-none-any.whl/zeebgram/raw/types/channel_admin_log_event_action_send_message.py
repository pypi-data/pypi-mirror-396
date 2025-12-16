
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


class ChannelAdminLogEventActionSendMessage(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``166``
        - ID: ``278F2868``

    Parameters:
        message (:obj:`Message <zeebgram.raw.base.Message>`):
            N/A

    """

    __slots__: List[str] = ["message"]

    ID = 0x278f2868
    QUALNAME = "types.ChannelAdminLogEventActionSendMessage"

    def __init__(self, *, message: "raw.base.Message") -> None:
        self.message = message  # Message

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChannelAdminLogEventActionSendMessage":
        # No flags
        
        message = TLObject.read(b)
        
        return ChannelAdminLogEventActionSendMessage(message=message)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.message.write())
        
        return b.getvalue()
