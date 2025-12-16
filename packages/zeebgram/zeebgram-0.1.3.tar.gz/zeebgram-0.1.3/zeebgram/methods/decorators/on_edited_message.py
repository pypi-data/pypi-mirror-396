
from typing import Callable

import zeebgram
from zeebgram.filters import Filter


class OnEditedMessage:
    def on_edited_message(
        self=None,
        filters=None,
        group: int = 0
    ) -> Callable:
        """Decorator for handling edited messages.

        This does the same thing as :meth:`~zeebgram.Client.add_handler` using the
        :obj:`~zeebgram.handlers.EditedMessageHandler`.

        Parameters:
            filters (:obj:`~zeebgram.filters`, *optional*):
                Pass one or more filters to allow only a subset of messages to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: Callable) -> Callable:
            if isinstance(self, zeebgram.Client):
                self.add_handler(zeebgram.handlers.EditedMessageHandler(func, filters), group)
            elif isinstance(self, Filter) or self is None:
                if not hasattr(func, "handlers"):
                    func.handlers = []

                func.handlers.append(
                    (
                        zeebgram.handlers.EditedMessageHandler(func, self),
                        group if filters is None else filters
                    )
                )

            return func

        return decorator
