
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


class InputStickeredMediaDocument(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.InputStickeredMedia`.

    Details:
        - Layer: ``166``
        - ID: ``438865B``

    Parameters:
        id (:obj:`InputDocument <zeebgram.raw.base.InputDocument>`):
            N/A

    """

    __slots__: List[str] = ["id"]

    ID = 0x438865b
    QUALNAME = "types.InputStickeredMediaDocument"

    def __init__(self, *, id: "raw.base.InputDocument") -> None:
        self.id = id  # InputDocument

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InputStickeredMediaDocument":
        # No flags
        
        id = TLObject.read(b)
        
        return InputStickeredMediaDocument(id=id)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.id.write())
        
        return b.getvalue()
