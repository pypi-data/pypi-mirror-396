from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from layrz_sdk.constants import UTC


class PushNotification(BaseModel):
  model_config = ConfigDict(validate_by_name=False, validate_by_alias=True, serialize_by_alias=True)

  pk: str = Field(..., description='The primary key of the push notification, is a UUID4 string')
  title: str = Field(..., description='The title of the push notification')
  message: str = Field(..., description='The message content of the push notification')
  timestamp: datetime = Field(
    ...,
    description='The timestamp when the notification was created',
    default_factory=lambda: datetime.now(UTC),
  )

  @field_serializer('timestamp', when_used='always')
  def serialize_timestamp(self, value: datetime) -> float:
    return value.timestamp()
