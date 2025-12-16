
from typing import Callable

import zeebgram
from zeebgram.filters import Filter


class OnChatJoinRequest:
    def on_chat_join_request(
        self=None,
        filters=None,
        group: int = 0
    ) -> Callable:
        """Decorator for handling chat join requests.

        This does the same thing as :meth:`~zeebgram.Client.add_handler` using the
        :obj:`~zeebgram.handlers.ChatJoinRequestHandler`.

        Parameters:
            filters (:obj:`~zeebgram.filters`, *optional*):
                Pass one or more filters to allow only a subset of updates to be passed in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: Callable) -> Callable:
            if isinstance(self, zeebgram.Client):
                self.add_handler(zeebgram.handlers.ChatJoinRequestHandler(func, filters), group)
            elif isinstance(self, Filter) or self is None:
                if not hasattr(func, "handlers"):
                    func.handlers = []

                func.handlers.append(
                    (
                        zeebgram.handlers.ChatJoinRequestHandler(func, self),
                        group if filters is None else filters
                    )
                )

            return func

        return decorator
