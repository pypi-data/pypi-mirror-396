
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


class PageBlockOrderedList(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.PageBlock`.

    Details:
        - Layer: ``166``
        - ID: ``9A8AE1E1``

    Parameters:
        items (List of :obj:`PageListOrderedItem <zeebgram.raw.base.PageListOrderedItem>`):
            N/A

    """

    __slots__: List[str] = ["items"]

    ID = 0x9a8ae1e1
    QUALNAME = "types.PageBlockOrderedList"

    def __init__(self, *, items: List["raw.base.PageListOrderedItem"]) -> None:
        self.items = items  # Vector<PageListOrderedItem>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PageBlockOrderedList":
        # No flags
        
        items = TLObject.read(b)
        
        return PageBlockOrderedList(items=items)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.items))
        
        return b.getvalue()
