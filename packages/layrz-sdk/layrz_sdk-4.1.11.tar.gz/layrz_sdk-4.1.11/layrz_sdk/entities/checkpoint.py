from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from .waypoint import Waypoint, WaypointRef


class CheckpointOperationMode(StrEnum):
  """Defines the operation mode of a checkpoint"""

  FLEX = 'FLEX'
  """ Defines a flexible operation mode for the checkpoint """

  STRICT = 'STRICT'
  """ Defines a strict operation mode for the checkpoint """


class Checkpoint(BaseModel):
  """Checkpoint entity definition"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(description='Checkpoint ID')
  asset_id: int = Field(description='Asset ID')
  waypoints: list[Waypoint] = Field(description='List of waypoints', default_factory=list)
  start_at: datetime = Field(description='Checkpoint start date')

  @field_serializer('start_at', when_used='always')
  def serialize_start_at(self, start_at: datetime) -> float:
    return start_at.timestamp()

  end_at: datetime = Field(description='Checkpoint end date')

  @field_serializer('end_at', when_used='always')
  def serialize_end_at(self, end_at: datetime) -> float:
    return end_at.timestamp()


class CheckpointRef(BaseModel):
  """Checkpoint reference entity definition"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(description='Checkpoint ID', alias='id')
  name: str = Field(description='Checkpoint name')
  waypoints: list[WaypointRef] = Field(description='List of waypoints', default_factory=list)

  operation_mode: CheckpointOperationMode = Field(
    ...,
    description='Checkpoint operation mode',
  )
