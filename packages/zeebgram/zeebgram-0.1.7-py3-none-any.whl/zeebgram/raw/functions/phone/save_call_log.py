
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


class SaveCallLog(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``166``
        - ID: ``41248786``

    Parameters:
        peer (:obj:`InputPhoneCall <zeebgram.raw.base.InputPhoneCall>`):
            N/A

        file (:obj:`InputFile <zeebgram.raw.base.InputFile>`):
            N/A

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "file"]

    ID = 0x41248786
    QUALNAME = "functions.phone.SaveCallLog"

    def __init__(self, *, peer: "raw.base.InputPhoneCall", file: "raw.base.InputFile") -> None:
        self.peer = peer  # InputPhoneCall
        self.file = file  # InputFile

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SaveCallLog":
        # No flags
        
        peer = TLObject.read(b)
        
        file = TLObject.read(b)
        
        return SaveCallLog(peer=peer, file=file)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.peer.write())
        
        b.write(self.file.write())
        
        return b.getvalue()
