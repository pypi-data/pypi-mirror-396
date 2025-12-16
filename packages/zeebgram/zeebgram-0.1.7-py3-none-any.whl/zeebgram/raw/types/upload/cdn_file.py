
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


class CdnFile(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.upload.CdnFile`.

    Details:
        - Layer: ``166``
        - ID: ``A99FCA4F``

    Parameters:
        bytes (``bytes``):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: zeebgram.raw.functions

        .. autosummary::
            :nosignatures:

            upload.GetCdnFile
    """

    __slots__: List[str] = ["bytes"]

    ID = 0xa99fca4f
    QUALNAME = "types.upload.CdnFile"

    def __init__(self, *, bytes: bytes) -> None:
        self.bytes = bytes  # bytes

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "CdnFile":
        # No flags
        
        bytes = Bytes.read(b)
        
        return CdnFile(bytes=bytes)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Bytes(self.bytes))
        
        return b.getvalue()
