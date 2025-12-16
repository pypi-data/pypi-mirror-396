
from typing import AsyncGenerator, Union, Optional

import zeebgram
from zeebgram import raw
from zeebgram import types


class GetAllStories:
    async def get_all_stories(
        self: "zeebgram.Client",
        next: Optional[bool] = None,
        hidden: Optional[bool] = None,
        state: Optional[str] = None,
    ) -> Optional[AsyncGenerator["types.Story", None]]:
        """Get all active stories.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            ``Generator``: On success, a generator yielding :obj:`~zeebgram.types.Story` objects is returned.

        Example:
            .. code-block:: python

                # Get all active story
                async for story in app.get_all_stories():
                    print(story)

        Raises:
            ValueError: In case of invalid arguments.
        """

        r = await self.invoke(
            raw.functions.stories.GetAllStories(
                next=next,
                hidden=hidden,
                state=state
            )
        )

        users = {i.id: i for i in r.users}
        chats = {i.id: i for i in r.chats}

        for peer_story in r.peer_stories:
            for story in peer_story.stories:
                yield await types.Story._parse(
                    self,
                    story,
                    users,
                    chats,
                    peer_story.peer
                )
