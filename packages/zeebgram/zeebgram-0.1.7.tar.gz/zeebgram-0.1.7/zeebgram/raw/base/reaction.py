
# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from zeebgram import raw
from zeebgram.raw.core import TLObject

Reaction = Union[raw.types.ReactionCustomEmoji, raw.types.ReactionEmoji, raw.types.ReactionEmpty]


# noinspection PyRedeclaration
class Reaction:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 3 constructors available.

        .. currentmodule:: zeebgram.raw.types

        .. autosummary::
            :nosignatures:

            ReactionCustomEmoji
            ReactionEmoji
            ReactionEmpty
    """

    QUALNAME = "zeebgram.raw.base.Reaction"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.zeebgram.org/telegram/base/reaction")
