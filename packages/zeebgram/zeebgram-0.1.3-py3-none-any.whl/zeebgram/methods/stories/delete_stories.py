
from typing import List, Union, Iterable

import zeebgram
from zeebgram import raw
from zeebgram import types


class DeleteStories:
    async def delete_stories(
        self: "zeebgram.Client",
        chat_id: Union[int, str],
        story_ids: Union[int, Iterable[int]],
    ) -> List[int]:
        """Delete stories.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            story_ids (``int`` | ``list``):
                Unique identifier (int) or list of unique identifiers (list of int) for the target stories.

        Returns:
            List of ``int``: List of deleted stories IDs

        Example:
            .. code-block:: python

                # Delete a single story
                app.delete_stories(chat_id, 1)

                # Delete multiple stories
                app.delete_stories(chat_id, [1, 2])
        """
        is_iterable = not isinstance(story_ids, int)
        ids = list(story_ids) if is_iterable else [story_ids]

        r = await self.invoke(
            raw.functions.stories.DeleteStories(
                peer=await self.resolve_peer(chat_id),
                id=ids
            )
        )

        return types.List(r)
