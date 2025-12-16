
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


class PageCaption(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.PageCaption`.

    Details:
        - Layer: ``166``
        - ID: ``6F747657``

    Parameters:
        text (:obj:`RichText <zeebgram.raw.base.RichText>`):
            N/A

        credit (:obj:`RichText <zeebgram.raw.base.RichText>`):
            N/A

    """

    __slots__: List[str] = ["text", "credit"]

    ID = 0x6f747657
    QUALNAME = "types.PageCaption"

    def __init__(self, *, text: "raw.base.RichText", credit: "raw.base.RichText") -> None:
        self.text = text  # RichText
        self.credit = credit  # RichText

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PageCaption":
        # No flags
        
        text = TLObject.read(b)
        
        credit = TLObject.read(b)
        
        return PageCaption(text=text, credit=credit)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.text.write())
        
        b.write(self.credit.write())
        
        return b.getvalue()
