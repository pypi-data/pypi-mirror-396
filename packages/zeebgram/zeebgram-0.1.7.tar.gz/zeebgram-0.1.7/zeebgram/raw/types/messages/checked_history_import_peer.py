
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


class CheckedHistoryImportPeer(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.messages.CheckedHistoryImportPeer`.

    Details:
        - Layer: ``166``
        - ID: ``A24DE717``

    Parameters:
        confirm_text (``str``):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: zeebgram.raw.functions

        .. autosummary::
            :nosignatures:

            messages.CheckHistoryImportPeer
    """

    __slots__: List[str] = ["confirm_text"]

    ID = 0xa24de717
    QUALNAME = "types.messages.CheckedHistoryImportPeer"

    def __init__(self, *, confirm_text: str) -> None:
        self.confirm_text = confirm_text  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "CheckedHistoryImportPeer":
        # No flags
        
        confirm_text = String.read(b)
        
        return CheckedHistoryImportPeer(confirm_text=confirm_text)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.confirm_text))
        
        return b.getvalue()
