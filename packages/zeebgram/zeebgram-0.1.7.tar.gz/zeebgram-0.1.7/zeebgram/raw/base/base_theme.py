
# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from zeebgram import raw
from zeebgram.raw.core import TLObject

BaseTheme = Union[raw.types.BaseThemeArctic, raw.types.BaseThemeClassic, raw.types.BaseThemeDay, raw.types.BaseThemeNight, raw.types.BaseThemeTinted]


# noinspection PyRedeclaration
class BaseTheme:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 5 constructors available.

        .. currentmodule:: zeebgram.raw.types

        .. autosummary::
            :nosignatures:

            BaseThemeArctic
            BaseThemeClassic
            BaseThemeDay
            BaseThemeNight
            BaseThemeTinted
    """

    QUALNAME = "zeebgram.raw.base.BaseTheme"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.zeebgram.org/telegram/base/base-theme")
