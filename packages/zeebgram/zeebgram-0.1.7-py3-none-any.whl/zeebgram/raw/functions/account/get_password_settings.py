
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


class GetPasswordSettings(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``166``
        - ID: ``9CD4EAF9``

    Parameters:
        password (:obj:`InputCheckPasswordSRP <zeebgram.raw.base.InputCheckPasswordSRP>`):
            N/A

    Returns:
        :obj:`account.PasswordSettings <zeebgram.raw.base.account.PasswordSettings>`
    """

    __slots__: List[str] = ["password"]

    ID = 0x9cd4eaf9
    QUALNAME = "functions.account.GetPasswordSettings"

    def __init__(self, *, password: "raw.base.InputCheckPasswordSRP") -> None:
        self.password = password  # InputCheckPasswordSRP

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetPasswordSettings":
        # No flags
        
        password = TLObject.read(b)
        
        return GetPasswordSettings(password=password)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.password.write())
        
        return b.getvalue()
