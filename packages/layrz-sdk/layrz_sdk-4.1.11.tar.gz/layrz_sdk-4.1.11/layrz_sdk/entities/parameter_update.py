from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_serializer, field_validator


class ParamData(BaseModel):
  value: Any | None = Field(default=None, description='The current value of the parameter.')
  updated_at: datetime = Field(..., description='The timestamp when the parameter was updated.')

  @field_serializer('updated_at', when_used='always')
  def serialize_updated_at(self, value: datetime) -> float:
    return value.timestamp()


class ParameterUpdate(BaseModel):
  asset_id: int = Field(..., description='The unique identifier for the asset.')
  parameters: dict[str, ParamData] = Field(
    default_factory=dict,
    description='A mapping of parameter names to their data.',
  )

  @field_validator('parameters', mode='before')
  def validate_parameter(cls, value: dict[str, Any]) -> dict[str, Any]:
    return {k.replace('__', '.'): v for k, v in value.items()}
