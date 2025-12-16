
# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from zeebgram import raw
from zeebgram.raw.core import TLObject

Difference = Union[raw.types.updates.Difference, raw.types.updates.DifferenceEmpty, raw.types.updates.DifferenceSlice, raw.types.updates.DifferenceTooLong]


# noinspection PyRedeclaration
class Difference:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 4 constructors available.

        .. currentmodule:: zeebgram.raw.types

        .. autosummary::
            :nosignatures:

            updates.Difference
            updates.DifferenceEmpty
            updates.DifferenceSlice
            updates.DifferenceTooLong

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: zeebgram.raw.functions

        .. autosummary::
            :nosignatures:

            updates.GetDifference
    """

    QUALNAME = "zeebgram.raw.base.updates.Difference"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.zeebgram.org/telegram/base/difference")
