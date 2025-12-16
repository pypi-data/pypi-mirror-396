
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


class InviteToGroupCall(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``166``
        - ID: ``7B393160``

    Parameters:
        call (:obj:`InputGroupCall <zeebgram.raw.base.InputGroupCall>`):
            N/A

        users (List of :obj:`InputUser <zeebgram.raw.base.InputUser>`):
            N/A

    Returns:
        :obj:`Updates <zeebgram.raw.base.Updates>`
    """

    __slots__: List[str] = ["call", "users"]

    ID = 0x7b393160
    QUALNAME = "functions.phone.InviteToGroupCall"

    def __init__(self, *, call: "raw.base.InputGroupCall", users: List["raw.base.InputUser"]) -> None:
        self.call = call  # InputGroupCall
        self.users = users  # Vector<InputUser>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InviteToGroupCall":
        # No flags
        
        call = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return InviteToGroupCall(call=call, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.call.write())
        
        b.write(Vector(self.users))
        
        return b.getvalue()
