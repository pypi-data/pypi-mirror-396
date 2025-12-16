from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from .geofence import Geofence
from .message import Message
from .presence_type import PresenceType
from .trigger import Trigger


class Event(BaseModel):
  """Event entity definition"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    description='Event ID',
    alias='id',
  )
  trigger: Trigger = Field(description='Event trigger')
  asset_id: int = Field(description='Asset ID')
  message: Message = Field(description='Message')
  activated_at: datetime = Field(description='Event activation date')

  @field_serializer('activated_at', when_used='always')
  def serialize_activated_at(self, activated_at: datetime) -> float:
    return activated_at.timestamp()

  geofence: Geofence | None = Field(default=None, description='Geofence object')
  presence_type: PresenceType | None = Field(default=None, description='Presence type object')

  @field_serializer('presence_type', when_used='always')
  def serialize_presence_type(self, presence_type: PresenceType | None) -> str | None:
    return presence_type.value if presence_type else None
