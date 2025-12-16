
# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from zeebgram import raw
from zeebgram.raw.core import TLObject

CodeType = Union[raw.types.auth.CodeTypeCall, raw.types.auth.CodeTypeFlashCall, raw.types.auth.CodeTypeFragmentSms, raw.types.auth.CodeTypeMissedCall, raw.types.auth.CodeTypeSms]


# noinspection PyRedeclaration
class CodeType:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 5 constructors available.

        .. currentmodule:: zeebgram.raw.types

        .. autosummary::
            :nosignatures:

            auth.CodeTypeCall
            auth.CodeTypeFlashCall
            auth.CodeTypeFragmentSms
            auth.CodeTypeMissedCall
            auth.CodeTypeSms
    """

    QUALNAME = "zeebgram.raw.base.auth.CodeType"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.zeebgram.org/telegram/base/code-type")
