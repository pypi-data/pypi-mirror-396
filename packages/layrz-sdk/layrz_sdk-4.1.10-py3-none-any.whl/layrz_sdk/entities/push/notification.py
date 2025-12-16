from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PushNotification(BaseModel):
  model_config = ConfigDict(validate_by_name=False, validate_by_alias=True, serialize_by_alias=True)

  title: str = Field(..., description='The title of the push notification')
  message: str = Field(..., description='The message content of the push notification')
  timestamp: datetime = Field(..., description='The timestamp when the notification was created')
