
# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from zeebgram import raw
from zeebgram.raw.core import TLObject

ChannelParticipantsFilter = Union[raw.types.ChannelParticipantsAdmins, raw.types.ChannelParticipantsBanned, raw.types.ChannelParticipantsBots, raw.types.ChannelParticipantsContacts, raw.types.ChannelParticipantsKicked, raw.types.ChannelParticipantsMentions, raw.types.ChannelParticipantsRecent, raw.types.ChannelParticipantsSearch]


# noinspection PyRedeclaration
class ChannelParticipantsFilter:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 8 constructors available.

        .. currentmodule:: zeebgram.raw.types

        .. autosummary::
            :nosignatures:

            ChannelParticipantsAdmins
            ChannelParticipantsBanned
            ChannelParticipantsBots
            ChannelParticipantsContacts
            ChannelParticipantsKicked
            ChannelParticipantsMentions
            ChannelParticipantsRecent
            ChannelParticipantsSearch
    """

    QUALNAME = "zeebgram.raw.base.ChannelParticipantsFilter"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.zeebgram.org/telegram/base/channel-participants-filter")
