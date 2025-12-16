
from typing import Dict

import zeebgram
from zeebgram import raw
from zeebgram import types
from ..object import Object


class ChatAdminWithInviteLinks(Object):
    """Represents a chat administrator that has created invite links in a chat.

    Parameters:
        admin (:obj:`~zeebgram.types.User`):
            The administrator.

        chat_invite_links_count (``int``):
            The number of valid chat invite links created by this administrator.

        revoked_chat_invite_links_count (``int``):
            The number of revoked chat invite links created by this administrator.
    """

    def __init__(
        self, *,
        admin: "types.User",
        chat_invite_links_count: int,
        revoked_chat_invite_links_count: int = None
    ):
        super().__init__()

        self.admin = admin
        self.chat_invite_links_count = chat_invite_links_count
        self.revoked_chat_invite_links_count = revoked_chat_invite_links_count

    @staticmethod
    def _parse(
        client: "zeebgram.Client",
        admin: "raw.types.ChatAdminWithInvites",
        users: Dict[int, "raw.types.User"] = None
    ) -> "ChatAdminWithInviteLinks":
        return ChatAdminWithInviteLinks(
            admin=types.User._parse(client, users[admin.admin_id]),
            chat_invite_links_count=admin.invites_count,
            revoked_chat_invite_links_count=admin.revoked_invites_count
        )
