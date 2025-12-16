
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


class LangPackStringDeleted(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.LangPackString`.

    Details:
        - Layer: ``166``
        - ID: ``2979EEB2``

    Parameters:
        key (``str``):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: zeebgram.raw.functions

        .. autosummary::
            :nosignatures:

            langpack.GetStrings
    """

    __slots__: List[str] = ["key"]

    ID = 0x2979eeb2
    QUALNAME = "types.LangPackStringDeleted"

    def __init__(self, *, key: str) -> None:
        self.key = key  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "LangPackStringDeleted":
        # No flags
        
        key = String.read(b)
        
        return LangPackStringDeleted(key=key)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.key))
        
        return b.getvalue()
