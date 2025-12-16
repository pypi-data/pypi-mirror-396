
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


class JsonArray(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~zeebgram.raw.base.JSONValue`.

    Details:
        - Layer: ``166``
        - ID: ``F7444763``

    Parameters:
        value (List of :obj:`JSONValue <zeebgram.raw.base.JSONValue>`):
            N/A

    """

    __slots__: List[str] = ["value"]

    ID = 0xf7444763
    QUALNAME = "types.JsonArray"

    def __init__(self, *, value: List["raw.base.JSONValue"]) -> None:
        self.value = value  # Vector<JSONValue>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "JsonArray":
        # No flags
        
        value = TLObject.read(b)
        
        return JsonArray(value=value)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.value))
        
        return b.getvalue()
