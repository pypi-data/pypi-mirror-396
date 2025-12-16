
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


class PollAnswer(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.PollAnswer`.

    Details:
        - Layer: ``166``
        - ID: ``6CA9C2E9``

    Parameters:
        text (``str``):
            N/A

        option (``bytes``):
            N/A

    """

    __slots__: List[str] = ["text", "option"]

    ID = 0x6ca9c2e9
    QUALNAME = "types.PollAnswer"

    def __init__(self, *, text: str, option: bytes) -> None:
        self.text = text  # string
        self.option = option  # bytes

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PollAnswer":
        # No flags
        
        text = String.read(b)
        
        option = Bytes.read(b)
        
        return PollAnswer(text=text, option=option)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.text))
        
        b.write(Bytes(self.option))
        
        return b.getvalue()
