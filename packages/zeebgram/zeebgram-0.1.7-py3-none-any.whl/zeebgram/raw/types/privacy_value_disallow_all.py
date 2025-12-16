
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


class PrivacyValueDisallowAll(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.PrivacyRule`.

    Details:
        - Layer: ``166``
        - ID: ``8B73E763``

    Parameters:
        No parameters required.

    """

    __slots__: List[str] = []

    ID = 0x8b73e763
    QUALNAME = "types.PrivacyValueDisallowAll"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PrivacyValueDisallowAll":
        # No flags
        
        return PrivacyValueDisallowAll()

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        return b.getvalue()
