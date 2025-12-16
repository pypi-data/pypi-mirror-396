
from typing import Optional, List

import zeebgram
from zeebgram import raw, types
from ..object import Object


class MessageReactions(Object):
    """Contains information about a message reactions.

    Parameters:
        reactions (List of :obj:`~zeebgram.types.Reaction`):
            Reactions list.
    """

    def __init__(
        self,
        *,
        client: "zeebgram.Client" = None,
        reactions: Optional[List["types.Reaction"]] = None,
    ):
        super().__init__(client)

        self.reactions = reactions

    @staticmethod
    def _parse(
        client: "zeebgram.Client",
        message_reactions: Optional["raw.base.MessageReactions"] = None
    ) -> Optional["MessageReactions"]:
        if not message_reactions:
            return None

        return MessageReactions(
            client=client,
            reactions=[types.Reaction._parse_count(client, reaction)
                       for reaction in message_reactions.results]
        )
