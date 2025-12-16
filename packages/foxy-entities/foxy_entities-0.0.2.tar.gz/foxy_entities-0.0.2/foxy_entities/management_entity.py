from typing import Self, Type, TypeVar

from foxy_entities.abc import SocialMediaEntity
from foxy_entities.exceptions import (
    EntityTypeException,
    PresenceObjectException,
    BanningAbcClass,
)

SocialMediaEntityType = TypeVar("SocialMediaEntityType", bound="SocialMediaEntity")


class EntitiesController:
    """
    A virtual storage controller class that provides methods
    for adding and retrieving entities with simple Round Robin balancing
    """

    def __init__(self) -> None:
        self.__entity_virtual_storage: dict[str, list[SocialMediaEntity]] = {}

    def get_virtual_storage(self) -> dict[str, list[SocialMediaEntity]]:
        return self.__entity_virtual_storage.copy()

    @staticmethod
    def update_sequence_entity(
        sequence_entity: list[SocialMediaEntity], social_media_entity: SocialMediaEntity
    ) -> list[SocialMediaEntity]:
        sequence_entity = [social_media_entity] + sequence_entity
        return sequence_entity

    def add_entity(self, social_media_entity: SocialMediaEntity) -> Self:
        if not isinstance(social_media_entity, SocialMediaEntity):
            raise EntityTypeException(social_media_entity)
        if type(social_media_entity) is SocialMediaEntity:
            raise BanningAbcClass()
        sequence_entity = self.__entity_virtual_storage.get(
            social_media_entity.__class__.__name__
        )
        if sequence_entity is not None:
            self.__entity_virtual_storage[social_media_entity.__class__.__name__] = (
                self.update_sequence_entity(sequence_entity, social_media_entity)
            )
        else:
            self.__entity_virtual_storage[social_media_entity.__class__.__name__] = [
                social_media_entity
            ]
        return self

    def get_entity(
        self, social_media_type: Type[SocialMediaEntityType]
    ) -> SocialMediaEntityType:
        if not issubclass(social_media_type, SocialMediaEntity):
            raise EntityTypeException(social_media_type)
        if social_media_type is SocialMediaEntity:
            raise BanningAbcClass()

        sequence_entity = self.__entity_virtual_storage.get(social_media_type.__name__)

        if not sequence_entity:
            raise PresenceObjectException(social_media_type)

        social_media_entity = sequence_entity.pop()

        if sequence_entity:
            self.__entity_virtual_storage[social_media_type.__name__] = sequence_entity
        else:
            del self.__entity_virtual_storage[social_media_type.__name__]

        return social_media_entity
