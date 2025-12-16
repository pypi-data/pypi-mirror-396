
# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from zeebgram import raw
from zeebgram.raw.core import TLObject

SavedRingtone = Union[raw.types.account.SavedRingtone, raw.types.account.SavedRingtoneConverted]


# noinspection PyRedeclaration
class SavedRingtone:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 2 constructors available.

        .. currentmodule:: zeebgram.raw.types

        .. autosummary::
            :nosignatures:

            account.SavedRingtone
            account.SavedRingtoneConverted

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: zeebgram.raw.functions

        .. autosummary::
            :nosignatures:

            account.SaveRingtone
    """

    QUALNAME = "zeebgram.raw.base.account.SavedRingtone"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.zeebgram.org/telegram/base/saved-ringtone")
