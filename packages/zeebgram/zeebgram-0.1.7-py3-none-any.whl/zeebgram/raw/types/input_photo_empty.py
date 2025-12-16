
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


class InputPhotoEmpty(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.InputPhoto`.

    Details:
        - Layer: ``166``
        - ID: ``1CD7BF0D``

    Parameters:
        No parameters required.

    """

    __slots__: List[str] = []

    ID = 0x1cd7bf0d
    QUALNAME = "types.InputPhotoEmpty"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InputPhotoEmpty":
        # No flags
        
        return InputPhotoEmpty()

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        return b.getvalue()
