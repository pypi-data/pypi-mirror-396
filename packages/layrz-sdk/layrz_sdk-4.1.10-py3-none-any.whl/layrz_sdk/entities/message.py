from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from layrz_sdk.constants import UTC
from layrz_sdk.entities.geofence import Geofence
from layrz_sdk.entities.position import Position


class Message(BaseModel):
  """Message definition"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    ...,
    description='Message ID',
    alias='id',
  )
  asset_id: int = Field(..., description='Asset ID')
  position: Position = Field(
    default_factory=lambda: Position(),
    description='Current position of the device',
  )
  payload: dict[str, Any] = Field(
    default_factory=dict,
    description='Payload data of the device message',
  )
  sensors: dict[str, Any] = Field(
    default_factory=dict,
    description='Sensor data of the device message',
  )
  received_at: datetime = Field(
    default_factory=lambda: datetime.now(UTC),
    description='Timestamp when the message was received',
  )

  @field_serializer('received_at', when_used='always')
  def serialize_received_at(self, value: datetime) -> float:
    """Serialize received_at to a timestamp."""
    return value.timestamp()

  geofences: list[Geofence] = Field(
    default_factory=list,
    description='List of geofences associated with the message',
  )

  @field_validator('geofences', mode='before')
  def _validate_geofences(cls, value: Any) -> list[Geofence]:
    """Validate geofences"""
    if value is None:
      return []

    if not isinstance(value, list):
      return []

    return value
