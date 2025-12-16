from typing import Any


class EntityTypeException(Exception):
    """The value does not correspond to the abc class SocialMediaEntity"""

    def __init__(self, message: Any) -> None:
        self.message = (
            f"{message} does not correspond to the abc class SocialMediaEntity"
        )

    def __str__(self) -> str:
        return self.message


class PresenceObjectException(Exception):
    """There are no entities of the passed type"""

    def __init__(self, message: Any) -> None:
        self.message = f"There is no essential {message} type"

    def __str__(self) -> str:
        return self.message


class BanningAbcClass(Exception):
    """It is forbidden to transmit abc SocialMediaEntity"""

    def __str__(self) -> str:
        return "It is forbidden to transmit abc SocialMediaEntity"
