from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class OutboundService(BaseModel):
  """Outbound service definition"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    description='Service ID',
    alias='id',
  )
  name: str = Field(description='Service name')

  protocol_name: str | None = Field(
    default=None,
    description='Protocol name',
  )
  mqtt_topic: str | None = Field(
    default=None,
    description='MQTT topic for the service',
  )
  is_consumpted: bool = Field(
    default=False,
    description='Is the service consumpted',
  )
  credentials: dict[str, Any] = Field(
    description='Service credentials',
    default_factory=dict,
  )
