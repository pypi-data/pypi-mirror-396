
# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from zeebgram import raw
from zeebgram.raw.core import TLObject

ChannelParticipant = Union[raw.types.ChannelParticipant, raw.types.ChannelParticipantAdmin, raw.types.ChannelParticipantBanned, raw.types.ChannelParticipantCreator, raw.types.ChannelParticipantLeft, raw.types.ChannelParticipantSelf]


# noinspection PyRedeclaration
class ChannelParticipant:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 6 constructors available.

        .. currentmodule:: zeebgram.raw.types

        .. autosummary::
            :nosignatures:

            ChannelParticipant
            ChannelParticipantAdmin
            ChannelParticipantBanned
            ChannelParticipantCreator
            ChannelParticipantLeft
            ChannelParticipantSelf
    """

    QUALNAME = "zeebgram.raw.base.ChannelParticipant"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.zeebgram.org/telegram/base/channel-participant")
