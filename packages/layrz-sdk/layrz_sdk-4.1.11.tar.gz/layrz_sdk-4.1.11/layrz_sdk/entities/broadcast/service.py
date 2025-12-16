"""Broadcast Service object"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BroadcastService(BaseModel):
  """Broadcast Service object"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    ...,
    description='Service ID',
    alias='id',
  )
  name: str = Field(..., description='Service name')
  credentials: dict[str, Any] = Field(default_factory=dict, description='Service credentials')
