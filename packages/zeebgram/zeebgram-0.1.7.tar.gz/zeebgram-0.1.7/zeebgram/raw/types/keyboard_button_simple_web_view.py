
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


class KeyboardButtonSimpleWebView(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.KeyboardButton`.

    Details:
        - Layer: ``166``
        - ID: ``A0C0505C``

    Parameters:
        text (``str``):
            N/A

        url (``str``):
            N/A

    """

    __slots__: List[str] = ["text", "url"]

    ID = 0xa0c0505c
    QUALNAME = "types.KeyboardButtonSimpleWebView"

    def __init__(self, *, text: str, url: str) -> None:
        self.text = text  # string
        self.url = url  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "KeyboardButtonSimpleWebView":
        # No flags
        
        text = String.read(b)
        
        url = String.read(b)
        
        return KeyboardButtonSimpleWebView(text=text, url=url)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.text))
        
        b.write(String(self.url))
        
        return b.getvalue()
