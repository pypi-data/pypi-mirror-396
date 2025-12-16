
from typing import Union

import zeebgram
from zeebgram import raw
from zeebgram import types


class GetBoosts:
    async def get_boosts(
        self: "zeebgram.Client",
    ) -> bool:
        """Get your boosts list

        .. include:: /_includes/usable-by/users-bots.rst

        Returns:
            List of :obj:`~zeebgram.types.MyBoost`: On success.

        Example:
            .. code-block:: python

                # get boosts list
                app.get_boosts()
        """
        r = await self.invoke(
            raw.functions.premium.GetMyBoosts()
        )

        users = {i.id: i for i in r.users}
        chats = {i.id: i for i in r.chats}

        return types.List(
            types.MyBoost._parse(
                self,
                boost,
                users,
                chats,
            ) for boost in r.my_boosts
        )
