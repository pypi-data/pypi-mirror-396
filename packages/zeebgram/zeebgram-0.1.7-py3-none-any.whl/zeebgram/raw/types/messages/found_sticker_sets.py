
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


class FoundStickerSets(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.messages.FoundStickerSets`.

    Details:
        - Layer: ``166``
        - ID: ``8AF09DD2``

    Parameters:
        hash (``int`` ``64-bit``):
            N/A

        sets (List of :obj:`StickerSetCovered <zeebgram.raw.base.StickerSetCovered>`):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: zeebgram.raw.functions

        .. autosummary::
            :nosignatures:

            messages.SearchStickerSets
    """

    __slots__: List[str] = ["hash", "sets"]

    ID = 0x8af09dd2
    QUALNAME = "types.messages.FoundStickerSets"

    def __init__(self, *, hash: int, sets: List["raw.base.StickerSetCovered"]) -> None:
        self.hash = hash  # long
        self.sets = sets  # Vector<StickerSetCovered>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "FoundStickerSets":
        # No flags
        
        hash = Long.read(b)
        
        sets = TLObject.read(b)
        
        return FoundStickerSets(hash=hash, sets=sets)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.hash))
        
        b.write(Vector(self.sets))
        
        return b.getvalue()
