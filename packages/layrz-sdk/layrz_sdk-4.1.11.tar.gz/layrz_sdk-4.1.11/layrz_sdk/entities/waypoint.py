from datetime import datetime, timedelta
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from .geofence import Geofence


class WaypointKind(StrEnum):
  PATHWAY = 'PATHWAY'
  """ This is the identification of the time between one waypoint and other """

  POINT = 'POINT'
  """ This refer the time inside of a geofence """

  DOWNLOADING = 'DOWNLOADING'
  """ Downloading phase of Tenvio """

  WASHING = 'WASHING'
  """ Washing phase of Tenvio """


class Waypoint(BaseModel):
  """Waypoint entity definition"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    description='Waypoint ID',
    alias='id',
  )
  geofence: Geofence | None = Field(default=None, description='Geofence object')
  geofence_id: int | None = Field(default=None, description='Geofence ID')
  start_at: datetime | None = Field(default=None, description='Waypoint start date')

  @field_serializer('start_at', when_used='always')
  def serialize_start_at(self, value: datetime | None) -> float | None:
    return value.timestamp() if value else None

  end_at: datetime | None = Field(default=None, description='Waypoint end date')

  @field_serializer('end_at', when_used='always')
  def serialize_end_at(self, value: datetime | None) -> float | None:
    return value.timestamp() if value else None

  sequence_real: int = Field(..., description='Real sequence number')
  sequence_ideal: int = Field(..., description='Ideal sequence number')


class WaypointRef(BaseModel):
  """Waypoint reference entity definition"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    description='Waypoint ID',
    alias='id',
  )
  geofence_id: int = Field(description='Geofence ID')
  time: timedelta = Field(
    default_factory=lambda: timedelta(seconds=0),
    description='Time offset from the start of the checkpoint',
  )

  @field_serializer('time', when_used='always')
  def serialize_time(self, value: timedelta) -> float:
    return value.total_seconds()

  kind: WaypointKind = Field(
    ...,
    description='Defines the kind of waypoint',
  )

  @field_serializer('kind', when_used='always')
  def serialize_kind(self, value: WaypointKind) -> str:
    return value.value
