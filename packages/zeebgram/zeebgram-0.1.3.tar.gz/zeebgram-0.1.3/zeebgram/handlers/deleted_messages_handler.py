
from typing import List, Callable

import zeebgram
from zeebgram.filters import Filter
from zeebgram.types import Message
from .handler import Handler


class DeletedMessagesHandler(Handler):
    """The deleted messages handler class. Used to handle deleted messages coming from any chat
    (private, group, channel). It is intended to be used with :meth:`~zeebgram.Client.add_handler`

    For a nicer way to register this handler, have a look at the
    :meth:`~zeebgram.Client.on_deleted_messages` decorator.

    Parameters:
        callback (``Callable``):
            Pass a function that will be called when one or more messages have been deleted.
            It takes *(client, messages)* as positional arguments (look at the section below for a detailed description).

        filters (:obj:`Filters`):
            Pass one or more filters to allow only a subset of messages to be passed
            in your callback function.

    Other parameters:
        client (:obj:`~zeebgram.Client`):
            The Client itself, useful when you want to call other API methods inside the message handler.

        messages (List of :obj:`~zeebgram.types.Message`):
            The deleted messages, as list.
    """

    def __init__(self, callback: Callable, filters: Filter = None):
        super().__init__(callback, filters)

    async def check(self, client: "zeebgram.Client", messages: List[Message]):
        # Every message should be checked, if at least one matches the filter True is returned
        # otherwise, or if the list is empty, False is returned
        for message in messages:
            if await super().check(client, message):
                return True
        else:
            return False
