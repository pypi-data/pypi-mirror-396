
# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from zeebgram import raw
from zeebgram.raw.core import TLObject

RequestPeerType = Union[raw.types.RequestPeerTypeBroadcast, raw.types.RequestPeerTypeChat, raw.types.RequestPeerTypeUser]


# noinspection PyRedeclaration
class RequestPeerType:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 3 constructors available.

        .. currentmodule:: zeebgram.raw.types

        .. autosummary::
            :nosignatures:

            RequestPeerTypeBroadcast
            RequestPeerTypeChat
            RequestPeerTypeUser
    """

    QUALNAME = "zeebgram.raw.base.RequestPeerType"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.zeebgram.org/telegram/base/request-peer-type")
