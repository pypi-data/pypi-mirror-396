from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class AtsPossibleExit(BaseModel):
  """AtsPossibleExit entity"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    description='Defines the primary key of the AtsPossibleExit',
    alias='id',
  )

  identifier: int | None = Field(
    default=None,
    description='Nullable positive big integer identifier for the exit',
  )

  # Volume / gauge snapshots
  initial_tank_volume: float | None = Field(
    default=None,
    description='Initial tank volume in liters',
  )
  initial_fluxometer: float | None = Field(
    default=None,
    description='Initial fluxometer reading in liters',
  )
  total_liters: float = Field(
    default=0.0,
    description='Total liters of fuel involved in the exit',
  )

  # Status flags
  is_ready: bool = Field(
    default=False,
    description='Indicates if the exit is ready',
  )
  in_progress: bool = Field(
    default=False,
    description='Indicates if the exit is in progress',
  )
  is_validated: bool = Field(
    default=False,
    description='Indicates if the exit is validated',
  )

  # Lifecycle timestamps
  start_at: datetime = Field(
    default_factory=datetime.now,
    description='Timestamp when the exit started',
  )

  @field_serializer('start_at', when_used='always')
  def serialize_start_at(self, start_at: datetime) -> float:
    return start_at.timestamp()

  end_at: datetime | None = Field(
    default=None,
    description='Timestamp when the exit ended',
  )

  @field_serializer('end_at', when_used='always')
  def serialize_end_at(self, end_at: datetime | None) -> float | None:
    return end_at.timestamp() if end_at else None

  # Derived / bookkeeping flags
  is_recalculated: bool = Field(
    default=False,
    description='Indicates if the exit has been recalculated',
  )
  is_blackbox: bool | None = Field(
    default=False,
    description='Indicates if the exit is a blackbox',
  )
  false_positive_count: int | None = Field(
    default=0,
    description='Count of false positives detected',
  )
