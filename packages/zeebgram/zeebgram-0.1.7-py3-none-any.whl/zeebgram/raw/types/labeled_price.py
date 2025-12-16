
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


class LabeledPrice(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.LabeledPrice`.

    Details:
        - Layer: ``166``
        - ID: ``CB296BF8``

    Parameters:
        label (``str``):
            N/A

        amount (``int`` ``64-bit``):
            N/A

    """

    __slots__: List[str] = ["label", "amount"]

    ID = 0xcb296bf8
    QUALNAME = "types.LabeledPrice"

    def __init__(self, *, label: str, amount: int) -> None:
        self.label = label  # string
        self.amount = amount  # long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "LabeledPrice":
        # No flags
        
        label = String.read(b)
        
        amount = Long.read(b)
        
        return LabeledPrice(label=label, amount=amount)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.label))
        
        b.write(Long(self.amount))
        
        return b.getvalue()
