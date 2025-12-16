import pytest

from foxy_entities import EntitiesController, SocialMediaEntity
from foxy_entities.exceptions import (
    EntityTypeException,
    BanningAbcClass,
    PresenceObjectException,
)
from tests.test_abc import TestSocialMediaEntity


@pytest.mark.parametrize(
    "input_value",
    [
        1,  # int
        0.2,  # float
        [1, 4, 5],  # list
        "hello",  # str
        True,  # bool
        None,  # NoneType
        (1, 2, 3),  # tuple
        {"key": "value"},  # dict
        {1, 2, 3},  # set
        3 + 4j,  # complex
        b"bytes",  # bytes
        bytearray(b"test"),  # bytearray
    ],
)
def test_exception_entity_type_add_entity(input_value):
    """
    Test case for checking the prohibition of transmission of
    a type that does not correspond to SocialMediaEntity
    """
    with pytest.raises(EntityTypeException):
        EntitiesController().add_entity(input_value)


def test_add_entity_incorrect_type_abc_class():
    """
    Test case prohibiting transfer of abc class
    """
    with pytest.raises(BanningAbcClass):
        EntitiesController().add_entity(SocialMediaEntity())


def test_add_entity_position():
    """
    Test case of how getting an entity in a FIFO queue works
    """
    entity_controller = EntitiesController()
    test_entity_1 = TestSocialMediaEntity(test_str="test_entity_1")
    test_entity_2 = TestSocialMediaEntity(test_str="test_entity_2")
    entity_controller.add_entity(test_entity_1).add_entity(test_entity_2)
    received_entity = entity_controller.get_entity(TestSocialMediaEntity)
    assert test_entity_1 == received_entity
    received_entity = entity_controller.get_entity(TestSocialMediaEntity)
    assert test_entity_2 == received_entity


def test_unique_sequences_objects():
    """
    Test case virtual storages should not overlap between different objects
    """
    entity_controller_1 = EntitiesController()
    entity_controller_2 = EntitiesController()
    test_entity_1 = TestSocialMediaEntity(test_str="test_entity_1")
    test_entity_2 = TestSocialMediaEntity(test_str="test_entity_2")
    entity_controller_1.add_entity(test_entity_1)
    entity_controller_2.add_entity(test_entity_2)
    assert (
        entity_controller_1.get_virtual_storage()
        != entity_controller_2.get_virtual_storage()
    )


@pytest.mark.parametrize(
    "input_value",
    [
        1,  # int
        0.2,  # float
        [1, 4, 5],  # list
        "hello",  # str
        True,  # bool
        None,  # NoneType
        (1, 2, 3),  # tuple
        {"key": "value"},  # dict
        {1, 2, 3},  # set
        3 + 4j,  # complex
        b"bytes",  # bytes
        bytearray(b"test"),  # bytearray
    ],
)
def test_get_entity_incorrect_type_base(input_value):
    """
    Test case virtual storages should not overlap between different objects
    """
    with pytest.raises(TypeError):
        EntitiesController().get_entity(input_value)


def test_get_entity_incorrect_type_abc_class():
    """
    Test case prohibiting transfer of abc class
    """
    with pytest.raises(BanningAbcClass):
        EntitiesController().get_entity(SocialMediaEntity)


def test_get_entity_out_stock():
    """
    Test case exceptions when the passed type is not in the virtual storage
    """
    with pytest.raises(PresenceObjectException):
        EntitiesController().get_entity(TestSocialMediaEntity)


def test_purge_virtual_storage():
    """
    Test case virtual storage must clear empty entity lists
    """
    entity_controller = EntitiesController()
    entity_controller.add_entity(TestSocialMediaEntity(test_str="test_entity_1"))
    entity_controller.get_entity(TestSocialMediaEntity)
    assert entity_controller.get_virtual_storage() == {}


def test_independence_virtual_storage():
    """
    Test case virtual storage must clear empty entity lists
    """
    entity_controller = EntitiesController()
    entity_controller.add_entity(TestSocialMediaEntity(test_str="test_entity_1"))
    entity_copy = entity_controller.get_virtual_storage()
    entity_copy["TestSocialMediaEntity2"] = [
        TestSocialMediaEntity(test_str="test_entity_2")
    ]
    assert entity_copy != entity_controller.get_virtual_storage()
