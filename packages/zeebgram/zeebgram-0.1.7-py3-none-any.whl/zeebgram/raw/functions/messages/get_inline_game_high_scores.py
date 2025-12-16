
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


class GetInlineGameHighScores(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``166``
        - ID: ``F635E1B``

    Parameters:
        id (:obj:`InputBotInlineMessageID <zeebgram.raw.base.InputBotInlineMessageID>`):
            N/A

        user_id (:obj:`InputUser <zeebgram.raw.base.InputUser>`):
            N/A

    Returns:
        :obj:`messages.HighScores <zeebgram.raw.base.messages.HighScores>`
    """

    __slots__: List[str] = ["id", "user_id"]

    ID = 0xf635e1b
    QUALNAME = "functions.messages.GetInlineGameHighScores"

    def __init__(self, *, id: "raw.base.InputBotInlineMessageID", user_id: "raw.base.InputUser") -> None:
        self.id = id  # InputBotInlineMessageID
        self.user_id = user_id  # InputUser

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetInlineGameHighScores":
        # No flags
        
        id = TLObject.read(b)
        
        user_id = TLObject.read(b)
        
        return GetInlineGameHighScores(id=id, user_id=user_id)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.id.write())
        
        b.write(self.user_id.write())
        
        return b.getvalue()
