
# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from zeebgram import raw
from zeebgram.raw.core import TLObject

GroupCall = Union[raw.types.phone.GroupCall]


# noinspection PyRedeclaration
class GroupCall:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 1 constructor available.

        .. currentmodule:: zeebgram.raw.types

        .. autosummary::
            :nosignatures:

            phone.GroupCall

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: zeebgram.raw.functions

        .. autosummary::
            :nosignatures:

            phone.GetGroupCall
    """

    QUALNAME = "zeebgram.raw.base.phone.GroupCall"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.zeebgram.org/telegram/base/group-call")
