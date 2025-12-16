
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


class EmailVerifyPurposeLoginSetup(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.EmailVerifyPurpose`.

    Details:
        - Layer: ``166``
        - ID: ``4345BE73``

    Parameters:
        phone_number (``str``):
            N/A

        phone_code_hash (``str``):
            N/A

    """

    __slots__: List[str] = ["phone_number", "phone_code_hash"]

    ID = 0x4345be73
    QUALNAME = "types.EmailVerifyPurposeLoginSetup"

    def __init__(self, *, phone_number: str, phone_code_hash: str) -> None:
        self.phone_number = phone_number  # string
        self.phone_code_hash = phone_code_hash  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "EmailVerifyPurposeLoginSetup":
        # No flags
        
        phone_number = String.read(b)
        
        phone_code_hash = String.read(b)
        
        return EmailVerifyPurposeLoginSetup(phone_number=phone_number, phone_code_hash=phone_code_hash)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.phone_number))
        
        b.write(String(self.phone_code_hash))
        
        return b.getvalue()
