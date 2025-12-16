
from uuid import uuid4

import zeebgram
from zeebgram import types
from ..object import Object


class InlineQueryResult(Object):
    """One result of an inline query.

    - :obj:`~zeebgram.types.InlineQueryResultCachedAudio`
    - :obj:`~zeebgram.types.InlineQueryResultCachedDocument`
    - :obj:`~zeebgram.types.InlineQueryResultCachedAnimation`
    - :obj:`~zeebgram.types.InlineQueryResultCachedPhoto`
    - :obj:`~zeebgram.types.InlineQueryResultCachedSticker`
    - :obj:`~zeebgram.types.InlineQueryResultCachedVideo`
    - :obj:`~zeebgram.types.InlineQueryResultCachedVoice`
    - :obj:`~zeebgram.types.InlineQueryResultArticle`
    - :obj:`~zeebgram.types.InlineQueryResultAudio`
    - :obj:`~zeebgram.types.InlineQueryResultContact`
    - :obj:`~zeebgram.types.InlineQueryResultDocument`
    - :obj:`~zeebgram.types.InlineQueryResultAnimation`
    - :obj:`~zeebgram.types.InlineQueryResultLocation`
    - :obj:`~zeebgram.types.InlineQueryResultPhoto`
    - :obj:`~zeebgram.types.InlineQueryResultVenue`
    - :obj:`~zeebgram.types.InlineQueryResultVideo`
    - :obj:`~zeebgram.types.InlineQueryResultVoice`
    """

    def __init__(
        self,
        type: str,
        id: str,
        input_message_content: "types.InputMessageContent",
        reply_markup: "types.InlineKeyboardMarkup"
    ):
        super().__init__()

        self.type = type
        self.id = str(uuid4()) if id is None else str(id)
        self.input_message_content = input_message_content
        self.reply_markup = reply_markup

    async def write(self, client: "zeebgram.Client"):
        pass
