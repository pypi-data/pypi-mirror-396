
from datetime import datetime
from typing import Dict

import zeebgram
from zeebgram import raw, utils
from zeebgram import types
from ..object import Object
from ..update import Update


class ChatJoinRequest(Object, Update):
    """Represents a join request sent to a chat.

    Parameters:
        chat (:obj:`~zeebgram.types.Chat`):
            Chat to which the request was sent.

        from_user (:obj:`~zeebgram.types.User`):
            User that sent the join request.

        date (:py:obj:`~datetime.datetime`):
            Date the request was sent.

        bio (``str``, *optional*):
            Bio of the user.

        invite_link (:obj:`~zeebgram.types.ChatInviteLink`, *optional*):
            Chat invite link that was used by the user to send the join request.
    """

    def __init__(
        self,
        *,
        client: "zeebgram.Client" = None,
        chat: "types.Chat",
        from_user: "types.User",
        date: datetime,
        bio: str = None,
        invite_link: "types.ChatInviteLink" = None
    ):
        super().__init__(client)

        self.chat = chat
        self.from_user = from_user
        self.date = date
        self.bio = bio
        self.invite_link = invite_link

    @staticmethod
    def _parse(
        client: "zeebgram.Client",
        update: "raw.types.UpdateBotChatInviteRequester",
        users: Dict[int, "raw.types.User"],
        chats: Dict[int, "raw.types.Chat"]
    ) -> "ChatJoinRequest":
        chat_id = utils.get_raw_peer_id(update.peer)

        return ChatJoinRequest(
            chat=types.Chat._parse_chat(client, chats[chat_id]),
            from_user=types.User._parse(client, users[update.user_id]),
            date=utils.timestamp_to_datetime(update.date),
            bio=update.about,
            invite_link=types.ChatInviteLink._parse(client, update.invite, users),
            client=client
        )

    async def approve(self) -> bool:
        """Bound method *approve* of :obj:`~zeebgram.types.ChatJoinRequest`.
        
        Use as a shortcut for:
        
        .. code-block:: python

            await client.approve_chat_join_request(
                chat_id=request.chat.id,
                user_id=request.from_user.id
            )
            
        Example:
            .. code-block:: python

                await request.approve()
                
        Returns:
            ``bool``: True on success.
        
        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.approve_chat_join_request(
            chat_id=self.chat.id,
            user_id=self.from_user.id
        )

    async def decline(self) -> bool:
        """Bound method *decline* of :obj:`~zeebgram.types.ChatJoinRequest`.
        
        Use as a shortcut for:
        
        .. code-block:: python

            await client.decline_chat_join_request(
                chat_id=request.chat.id,
                user_id=request.from_user.id
            )
            
        Example:
            .. code-block:: python

                await request.decline()
                
        Returns:
            ``bool``: True on success.
        
        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.decline_chat_join_request(
            chat_id=self.chat.id,
            user_id=self.from_user.id
        )
