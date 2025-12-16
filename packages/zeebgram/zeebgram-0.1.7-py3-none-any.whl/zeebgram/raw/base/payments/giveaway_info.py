
# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from zeebgram import raw
from zeebgram.raw.core import TLObject

GiveawayInfo = Union[raw.types.payments.GiveawayInfo, raw.types.payments.GiveawayInfoResults]


# noinspection PyRedeclaration
class GiveawayInfo:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 2 constructors available.

        .. currentmodule:: zeebgram.raw.types

        .. autosummary::
            :nosignatures:

            payments.GiveawayInfo
            payments.GiveawayInfoResults

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: zeebgram.raw.functions

        .. autosummary::
            :nosignatures:

            payments.GetGiveawayInfo
    """

    QUALNAME = "zeebgram.raw.base.payments.GiveawayInfo"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.zeebgram.org/telegram/base/giveaway-info")
