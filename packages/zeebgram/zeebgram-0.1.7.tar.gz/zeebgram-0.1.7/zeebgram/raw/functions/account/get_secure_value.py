
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


class GetSecureValue(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``166``
        - ID: ``73665BC2``

    Parameters:
        types (List of :obj:`SecureValueType <zeebgram.raw.base.SecureValueType>`):
            N/A

    Returns:
        List of :obj:`SecureValue <zeebgram.raw.base.SecureValue>`
    """

    __slots__: List[str] = ["types"]

    ID = 0x73665bc2
    QUALNAME = "functions.account.GetSecureValue"

    def __init__(self, *, types: List["raw.base.SecureValueType"]) -> None:
        self.types = types  # Vector<SecureValueType>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetSecureValue":
        # No flags
        
        types = TLObject.read(b)
        
        return GetSecureValue(types=types)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.types))
        
        return b.getvalue()
