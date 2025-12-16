from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class AtsExitExecutionHistory(BaseModel):
  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
    from_attributes=True,
  )
  pk: int = Field(
    description='Primary key of the Exit Execution History',
    alias='id',
  )

  from_asset_id: int = Field(description='ID of the asset from which the exit is initiated')
  to_asset_id: int = Field(description='ID of the asset to which the exit is directed')

  status: Literal['PENDING', 'FAILED', 'SUCCESS'] = Field(default='PENDING')

  from_app: Literal['ATSWEB', 'ATSMOBILE', 'NFC'] | None = Field(
    default=None,
    description='Application from which the exit was initiated',
  )

  error_response: str | None = Field(default=None, description='Error response received during the exit process')
  generated_by_id: int = Field(description='ID of the user or system that initiated the exit')
  queue_id: int | None = Field(default=None, description='ID of the queue associated with the exit')
  to_asset_mileage: float | None = Field(default=None, description='Mileage of the asset to which the exit is directed')

  created_at: datetime = Field(description='Timestamp when the exit was created')

  @field_serializer('created_at', when_used='always')
  def serialize_created_at(self, created_at: datetime) -> float:
    return created_at.timestamp()

  updated_at: datetime = Field(description='Timestamp when the exit was last updated')

  @field_serializer('updated_at', when_used='always')
  def serialize_updated_at(self, updated_at: datetime) -> float:
    return updated_at.timestamp()
