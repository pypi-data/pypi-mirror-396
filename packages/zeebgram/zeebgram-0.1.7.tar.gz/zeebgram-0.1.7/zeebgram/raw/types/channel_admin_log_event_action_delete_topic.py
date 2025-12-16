
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


class ChannelAdminLogEventActionDeleteTopic(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``166``
        - ID: ``AE168909``

    Parameters:
        topic (:obj:`ForumTopic <zeebgram.raw.base.ForumTopic>`):
            N/A

    """

    __slots__: List[str] = ["topic"]

    ID = 0xae168909
    QUALNAME = "types.ChannelAdminLogEventActionDeleteTopic"

    def __init__(self, *, topic: "raw.base.ForumTopic") -> None:
        self.topic = topic  # ForumTopic

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChannelAdminLogEventActionDeleteTopic":
        # No flags
        
        topic = TLObject.read(b)
        
        return ChannelAdminLogEventActionDeleteTopic(topic=topic)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.topic.write())
        
        return b.getvalue()
