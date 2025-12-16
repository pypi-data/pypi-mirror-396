
import zeebgram

from ..object import Object

"""- :obj:`~zeebgram.types.InputLocationMessageContent`
    - :obj:`~zeebgram.types.InputVenueMessageContent`
    - :obj:`~zeebgram.types.InputContactMessageContent`"""


class InputMessageContent(Object):
    """Content of a message to be sent as a result of an inline query.

    Pyrogram currently supports the following types:

    - :obj:`~zeebgram.types.InputTextMessageContent`
    """

    def __init__(self):
        super().__init__()

    async def write(self, client: "zeebgram.Client", reply_markup):
        raise NotImplementedError
