import uuid

from pydantic import BaseModel, Field


class SocialMediaEntity(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
