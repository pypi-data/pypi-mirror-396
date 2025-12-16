"""Module for decoding received webhook notifications from Fishjam."""

from typing import Union

import betterproto

from fishjam.events._protos.fishjam import ServerMessage
from fishjam.events.allowed_notifications import (
    ALLOWED_NOTIFICATIONS,
    AllowedNotification,
)


def receive_binary(binary: bytes) -> Union[AllowedNotification, None]:
    """Transforms a received protobuf notification into a notification instance.

    The available notifications are listed in `fishjam.events` module.

    Args:
        binary: The raw binary data received from the webhook.

    Returns:
        AllowedNotification | None: The parsed notification object, or None if
            the message type is not supported.
    """
    message = ServerMessage().parse(binary)
    _which, message = betterproto.which_one_of(message, "content")

    if isinstance(message, ALLOWED_NOTIFICATIONS):
        return message

    return None
