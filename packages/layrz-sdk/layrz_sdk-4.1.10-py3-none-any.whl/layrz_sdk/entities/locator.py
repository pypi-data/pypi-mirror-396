from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from .asset import Asset
from .geofence import Geofence
from .trigger import Trigger


class LocatorMqttConfig(BaseModel):
  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )
  host: str = Field(..., description='Defines the MQTT host of the locator')
  port: int = Field(..., description='Defines the MQTT port of the locator')
  username: str | None = Field(default=None, description='Defines the MQTT username of the locator')
  password: str | None = Field(default=None, description='Defines the MQTT password of the locator')
  topic: str = Field(..., description='Defines the MQTT topic of the locator')


class Locator(BaseModel):
  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )
  pk: str = Field(
    ...,
    description='Defines the primary key of the locator',
    alias='id',
  )

  @field_validator('pk', mode='before')
  def validate_pk(cls, v: Any) -> str:
    if isinstance(v, int):
      return str(v)
    if isinstance(v, str):
      return v
    if isinstance(v, UUID):
      return str(v)
    raise ValueError('Invalid type for pk')

  token: str = Field(..., description='Defines the token of the locator')
  owner_id: int = Field(..., description='Defines the owner ID of the locator')

  created_at: datetime = Field(..., description='Defines the creation date of the locator')

  @field_serializer('created_at', when_used='always')
  def serialize_created_at(self, created_at: datetime) -> float:
    return created_at.timestamp()

  updated_at: datetime = Field(..., description='Defines the last update date of the locator')

  @field_serializer('updated_at', when_used='always')
  def serialize_updated_at(self, updated_at: datetime) -> float:
    return updated_at.timestamp()

  mqtt_config: LocatorMqttConfig | None = Field(..., description='Defines the MQTT configuration of the locator')
  assets: list[Asset] = Field(
    default_factory=list,
    description='Defines the list of assets associated with the locator',
  )

  geofences: list[Geofence] = Field(
    default_factory=list,
    description='Defines the list of geofences associated with the locator',
  )

  triggers: list[Trigger] = Field(
    default_factory=list,
    description='Defines the list of triggers associated with the locator',
  )

  is_expired: bool = Field(
    default=False,
    description='Indicates whether the locator is expired',
  )

  expires_at: datetime | None = Field(
    default=None,
    description='Defines the expiration date of the locator, if applicable',
  )

  @field_serializer('expires_at', when_used='always')
  def serialize_expires_at(self, expires_at: datetime | None) -> float | None:
    return expires_at.timestamp() if expires_at else None

  customization_id: int | None = Field(
    default=None,
    description='Defines the customization ID associated with the locator, if applicable',
  )
