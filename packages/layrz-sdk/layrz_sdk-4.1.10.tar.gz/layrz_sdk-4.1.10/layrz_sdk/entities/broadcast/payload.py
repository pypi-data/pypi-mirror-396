"""Broadcast Payload data"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_serializer

from layrz_sdk.constants import UTC
from layrz_sdk.entities.asset import Asset
from layrz_sdk.entities.device import Device
from layrz_sdk.entities.locator import Locator
from layrz_sdk.entities.trigger import Trigger

from .service import BroadcastService


class BroadcastPayload(BaseModel):
  """Broadcast payload data, structure that is sent to the Outbound MQTT and other services"""

  asset: Asset = Field(..., description='Asset object')

  @field_serializer('asset', when_used='always')
  def serialize_asset(self, v: Asset) -> dict[str, Any]:
    return v.model_dump(mode='json', by_alias=True)

  primary_device: Device | None = Field(default=None, description='Primary device object')

  @field_serializer('primary_device', when_used='always')
  def serialize_primary_device(self, v: Device | None) -> dict[str, Any] | None:
    if v is None:
      return None
    return v.model_dump(mode='json', by_alias=True)

  trigger: Trigger | None = Field(default=None, description='Trigger object, if available')

  @field_serializer('trigger', when_used='always')
  def serialize_trigger(self, v: Trigger | None) -> dict[str, Any] | None:
    if v is None:
      return None
    return v.model_dump(mode='json', by_alias=True)

  message_id: int | str = Field(..., description='Message ID')
  service: BroadcastService | None = Field(default=None, description='Broadcast service object')

  @field_serializer('service', when_used='always')
  def serialize_service(self, v: BroadcastService | None) -> dict[str, Any] | None:
    if v is None:
      return None
    return v.model_dump(mode='json', by_alias=True)

  position: dict[str, Any] = Field(default_factory=dict, description='Position data, if available')
  sensors: dict[str, Any] = Field(default_factory=dict, description='Sensors data, if available')
  payload: dict[str, Any] = Field(default_factory=dict, description='Payload data, if available')
  received_at: datetime = Field(
    default_factory=lambda: datetime.now(UTC),
    description='Broadcast payload received date',
  )

  @field_serializer('received_at', when_used='always')
  def serialize_received_at(self, v: datetime) -> float:
    return v.timestamp()

  locator: Locator | None = Field(default=None, description='Locator object, if available')

  @field_serializer('locator', when_used='always')
  def serialize_locator(self, v: Locator | None) -> dict[str, Any] | None:
    if v is None:
      return None
    return v.model_dump(mode='json', by_alias=True)
