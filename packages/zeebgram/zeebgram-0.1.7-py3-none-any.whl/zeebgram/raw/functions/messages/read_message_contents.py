
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


class ReadMessageContents(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``166``
        - ID: ``36A73F77``

    Parameters:
        id (List of ``int`` ``32-bit``):
            N/A

    Returns:
        :obj:`messages.AffectedMessages <zeebgram.raw.base.messages.AffectedMessages>`
    """

    __slots__: List[str] = ["id"]

    ID = 0x36a73f77
    QUALNAME = "functions.messages.ReadMessageContents"

    def __init__(self, *, id: List[int]) -> None:
        self.id = id  # Vector<int>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ReadMessageContents":
        # No flags
        
        id = TLObject.read(b, Int)
        
        return ReadMessageContents(id=id)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.id, Int))
        
        return b.getvalue()
