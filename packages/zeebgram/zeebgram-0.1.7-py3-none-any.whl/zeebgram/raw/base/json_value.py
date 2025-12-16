
# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from zeebgram import raw
from zeebgram.raw.core import TLObject

JSONValue = Union[raw.types.JsonArray, raw.types.JsonBool, raw.types.JsonNull, raw.types.JsonNumber, raw.types.JsonObject, raw.types.JsonString]


# noinspection PyRedeclaration
class JSONValue:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 6 constructors available.

        .. currentmodule:: zeebgram.raw.types

        .. autosummary::
            :nosignatures:

            JsonArray
            JsonBool
            JsonNull
            JsonNumber
            JsonObject
            JsonString
    """

    QUALNAME = "zeebgram.raw.base.JSONValue"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.zeebgram.org/telegram/base/json-value")
