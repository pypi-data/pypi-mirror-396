
# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from zeebgram import raw
from zeebgram.raw.core import TLObject

InputBotInlineResult = Union[raw.types.InputBotInlineResult, raw.types.InputBotInlineResultDocument, raw.types.InputBotInlineResultGame, raw.types.InputBotInlineResultPhoto]


# noinspection PyRedeclaration
class InputBotInlineResult:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 4 constructors available.

        .. currentmodule:: zeebgram.raw.types

        .. autosummary::
            :nosignatures:

            InputBotInlineResult
            InputBotInlineResultDocument
            InputBotInlineResultGame
            InputBotInlineResultPhoto
    """

    QUALNAME = "zeebgram.raw.base.InputBotInlineResult"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.zeebgram.org/telegram/base/input-bot-inline-result")
