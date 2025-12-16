import uuid

from foxy_entities import SocialMediaEntity


class TestSocialMediaEntity(SocialMediaEntity):
    test_str: str


class TestSocialMediaEntity2(SocialMediaEntity):
    test_str2: str


def test_id_social_media_entity():
    test_str = TestSocialMediaEntity(test_str="test_str")
    assert type(test_str.id) is uuid.UUID
