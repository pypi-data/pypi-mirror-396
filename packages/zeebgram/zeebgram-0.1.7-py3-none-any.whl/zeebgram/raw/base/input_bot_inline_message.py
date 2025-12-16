
# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from zeebgram import raw
from zeebgram.raw.core import TLObject

InputBotInlineMessage = Union[raw.types.InputBotInlineMessageGame, raw.types.InputBotInlineMessageMediaAuto, raw.types.InputBotInlineMessageMediaContact, raw.types.InputBotInlineMessageMediaGeo, raw.types.InputBotInlineMessageMediaInvoice, raw.types.InputBotInlineMessageMediaVenue, raw.types.InputBotInlineMessageMediaWebPage, raw.types.InputBotInlineMessageText]


# noinspection PyRedeclaration
class InputBotInlineMessage:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 8 constructors available.

        .. currentmodule:: zeebgram.raw.types

        .. autosummary::
            :nosignatures:

            InputBotInlineMessageGame
            InputBotInlineMessageMediaAuto
            InputBotInlineMessageMediaContact
            InputBotInlineMessageMediaGeo
            InputBotInlineMessageMediaInvoice
            InputBotInlineMessageMediaVenue
            InputBotInlineMessageMediaWebPage
            InputBotInlineMessageText
    """

    QUALNAME = "zeebgram.raw.base.InputBotInlineMessage"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.zeebgram.org/telegram/base/input-bot-inline-message")
