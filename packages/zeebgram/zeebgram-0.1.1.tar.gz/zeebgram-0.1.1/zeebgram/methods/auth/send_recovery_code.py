
import logging

import zeebgram
from zeebgram import raw

log = logging.getLogger(__name__)


class SendRecoveryCode:
    async def send_recovery_code(
        self: "zeebgram.Client",
    ) -> str:
        """Send a code to your email to recover your password.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            ``str``: On success, the hidden email pattern is returned and a recovery code is sent to that email.

        Raises:
            BadRequest: In case no recovery email was set up.
        """
        return (await self.invoke(
            raw.functions.auth.RequestPasswordRecovery()
        )).email_pattern
