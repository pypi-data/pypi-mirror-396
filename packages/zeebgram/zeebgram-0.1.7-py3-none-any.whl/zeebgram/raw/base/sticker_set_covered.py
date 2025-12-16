
# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from zeebgram import raw
from zeebgram.raw.core import TLObject

StickerSetCovered = Union[raw.types.StickerSetCovered, raw.types.StickerSetFullCovered, raw.types.StickerSetMultiCovered, raw.types.StickerSetNoCovered]


# noinspection PyRedeclaration
class StickerSetCovered:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 4 constructors available.

        .. currentmodule:: zeebgram.raw.types

        .. autosummary::
            :nosignatures:

            StickerSetCovered
            StickerSetFullCovered
            StickerSetMultiCovered
            StickerSetNoCovered

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: zeebgram.raw.functions

        .. autosummary::
            :nosignatures:

            messages.GetAttachedStickers
    """

    QUALNAME = "zeebgram.raw.base.StickerSetCovered"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.zeebgram.org/telegram/base/sticker-set-covered")
