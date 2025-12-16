from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from layrz_sdk.constants import UTC


class AtsReception(BaseModel):
  """AtsReception entity"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    description='Defines the primary key of the AtsReception',
    alias='id',
  )
  volume_bought: float = Field(
    description='Volume bought in liters',
    default=0.0,
  )
  real_volume: float | None = Field(
    description='Real volume in liters',
    default=None,
  )

  received_at: datetime = Field(
    description='Date and time when the reception was made',
    default_factory=lambda: datetime.now(UTC),
  )

  @field_serializer('received_at', when_used='always')
  def serialize_received_at(self, received_at: datetime) -> float:
    return received_at.timestamp()

  fuel_type: str = Field(
    description='Type of fuel used in the reception',
    default='',
  )
  is_merged: bool = Field(
    description='Indicates if the reception is merged with another',
    default=False,
  )
  order_id: int | None = Field(
    description='Order ID associated with the reception',
    default=None,
  )
