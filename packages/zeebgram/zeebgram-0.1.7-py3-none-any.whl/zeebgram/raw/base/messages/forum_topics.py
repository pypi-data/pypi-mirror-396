
# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from zeebgram import raw
from zeebgram.raw.core import TLObject

ForumTopics = Union[raw.types.messages.ForumTopics]


# noinspection PyRedeclaration
class ForumTopics:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 1 constructor available.

        .. currentmodule:: zeebgram.raw.types

        .. autosummary::
            :nosignatures:

            messages.ForumTopics

    Functions:
        This object can be returned by 2 functions.

        .. currentmodule:: zeebgram.raw.functions

        .. autosummary::
            :nosignatures:

            channels.GetForumTopics
            channels.GetForumTopicsByID
    """

    QUALNAME = "zeebgram.raw.base.messages.ForumTopics"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.zeebgram.org/telegram/base/forum-topics")
