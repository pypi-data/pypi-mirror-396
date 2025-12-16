
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


class GetChatsToSend(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``166``
        - ID: ``A56A8B60``

    Parameters:
        No parameters required.

    Returns:
        :obj:`messages.Chats <zeebgram.raw.base.messages.Chats>`
    """

    __slots__: List[str] = []

    ID = 0xa56a8b60
    QUALNAME = "functions.stories.GetChatsToSend"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetChatsToSend":
        # No flags
        
        return GetChatsToSend()

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        return b.getvalue()
