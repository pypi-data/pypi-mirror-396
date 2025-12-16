
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


class FavedStickers(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.messages.FavedStickers`.

    Details:
        - Layer: ``166``
        - ID: ``2CB51097``

    Parameters:
        hash (``int`` ``64-bit``):
            N/A

        packs (List of :obj:`StickerPack <zeebgram.raw.base.StickerPack>`):
            N/A

        stickers (List of :obj:`Document <zeebgram.raw.base.Document>`):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: zeebgram.raw.functions

        .. autosummary::
            :nosignatures:

            messages.GetFavedStickers
    """

    __slots__: List[str] = ["hash", "packs", "stickers"]

    ID = 0x2cb51097
    QUALNAME = "types.messages.FavedStickers"

    def __init__(self, *, hash: int, packs: List["raw.base.StickerPack"], stickers: List["raw.base.Document"]) -> None:
        self.hash = hash  # long
        self.packs = packs  # Vector<StickerPack>
        self.stickers = stickers  # Vector<Document>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "FavedStickers":
        # No flags
        
        hash = Long.read(b)
        
        packs = TLObject.read(b)
        
        stickers = TLObject.read(b)
        
        return FavedStickers(hash=hash, packs=packs, stickers=stickers)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.hash))
        
        b.write(Vector(self.packs))
        
        b.write(Vector(self.stickers))
        
        return b.getvalue()
