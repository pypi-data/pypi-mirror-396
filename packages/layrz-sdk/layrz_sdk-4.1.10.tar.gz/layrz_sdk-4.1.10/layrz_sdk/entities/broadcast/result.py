"""Broadcast result"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from .request import BroadcastRequest
from .response import BroadcastResponse
from .status import BroadcastStatus


class BroadcastResult(BaseModel):
  """Broadcast result data"""

  service_id: int = Field(description='Service ID')
  asset_id: int = Field(description='Asset ID')
  status: BroadcastStatus = Field(description='Broadcast status')
  request: BroadcastRequest = Field(description='Broadcast request')
  response: BroadcastResponse = Field(description='Broadcast response')
  submitted_at: datetime = Field(description='Broadcast submission date')


class RawBroadcastResult(BaseModel):
  """Broadcast result data"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int | None = Field(
    default=None,
    description='Broadcast result ID',
    alias='id',
  )

  trigger_id: int | None = Field(default=None, description='Trigger ID')
  service_id: int | None = Field(description='Service ID')
  asset_id: int | None = Field(description='Asset ID')

  status: BroadcastStatus = Field(description='Broadcast status')

  @field_serializer('status', when_used='always')
  def serialize_status(self, status: BroadcastStatus) -> str:
    return status.value

  algorithm: str | None = Field(
    default=None,
    description='Algorithm used for the broadcast, if any',
  )

  request: dict[str, Any] = Field(
    default_factory=dict,
    description='Broadcast request data',
  )

  response: dict[str, Any] = Field(
    default_factory=dict,
    description='Broadcast response data',
  )

  error: dict[str, Any] = Field(
    default_factory=dict,
    description='Error message if the broadcast failed',
  )

  service: dict[str, Any] = Field(
    default_factory=dict,
    description='Service details at the time of the broadcast',
  )

  asset: dict[str, Any] = Field(
    default_factory=dict,
    description='Asset details at the time of the broadcast',
  )

  trigger: dict[str, Any] = Field(
    default_factory=dict,
    description='Trigger details at the time of the broadcast',
  )

  submitted_at: datetime = Field(
    description='Broadcast submission date',
    alias='at',
  )

  @field_serializer('submitted_at', when_used='always')
  def serialize_submitted_at(self, v: datetime) -> float:
    return v.timestamp()
