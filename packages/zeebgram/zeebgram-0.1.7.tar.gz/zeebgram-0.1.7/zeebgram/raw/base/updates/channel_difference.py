
# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from zeebgram import raw
from zeebgram.raw.core import TLObject

ChannelDifference = Union[raw.types.updates.ChannelDifference, raw.types.updates.ChannelDifferenceEmpty, raw.types.updates.ChannelDifferenceTooLong]


# noinspection PyRedeclaration
class ChannelDifference:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 3 constructors available.

        .. currentmodule:: zeebgram.raw.types

        .. autosummary::
            :nosignatures:

            updates.ChannelDifference
            updates.ChannelDifferenceEmpty
            updates.ChannelDifferenceTooLong

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: zeebgram.raw.functions

        .. autosummary::
            :nosignatures:

            updates.GetChannelDifference
    """

    QUALNAME = "zeebgram.raw.base.updates.ChannelDifference"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.zeebgram.org/telegram/base/channel-difference")
