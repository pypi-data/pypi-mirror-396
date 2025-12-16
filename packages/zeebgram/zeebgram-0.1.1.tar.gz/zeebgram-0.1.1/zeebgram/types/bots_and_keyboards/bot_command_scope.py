
import zeebgram
from zeebgram import raw
from ..object import Object


class BotCommandScope(Object):
    """Represents the scope to which bot commands are applied.

    Currently, the following 7 scopes are supported:

    - :obj:`~zeebgram.types.BotCommandScopeDefault`
    - :obj:`~zeebgram.types.BotCommandScopeAllPrivateChats`
    - :obj:`~zeebgram.types.BotCommandScopeAllGroupChats`
    - :obj:`~zeebgram.types.BotCommandScopeAllChatAdministrators`
    - :obj:`~zeebgram.types.BotCommandScopeChat`
    - :obj:`~zeebgram.types.BotCommandScopeChatAdministrators`
    - :obj:`~zeebgram.types.BotCommandScopeChatMember`

    **Determining list of commands**

    The following algorithm is used to determine the list of commands for a particular user viewing the bot menu.
    The first list of commands which is set is returned:

    **Commands in the chat with the bot**:

    - BotCommandScopeChat + language_code
    - BotCommandScopeChat
    - BotCommandScopeAllPrivateChats + language_code
    - BotCommandScopeAllPrivateChats
    - BotCommandScopeDefault + language_code
    - BotCommandScopeDefault

    **Commands in group and supergroup chats**

    - BotCommandScopeChatMember + language_code
    - BotCommandScopeChatMember
    - BotCommandScopeChatAdministrators + language_code (administrators only)
    - BotCommandScopeChatAdministrators (administrators only)
    - BotCommandScopeChat + language_code
    - BotCommandScopeChat
    - BotCommandScopeAllChatAdministrators + language_code (administrators only)
    - BotCommandScopeAllChatAdministrators (administrators only)
    - BotCommandScopeAllGroupChats + language_code
    - BotCommandScopeAllGroupChats
    - BotCommandScopeDefault + language_code
    - BotCommandScopeDefault
    """

    def __init__(self, type: str):
        super().__init__()

        self.type = type

    async def write(self, client: "zeebgram.Client") -> "raw.base.BotCommandScope":
        raise NotImplementedError
