from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Geofence(BaseModel):
  """Geofence entity"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    ...,
    description='Defines the primary key of the geofence',
    alias='id',
  )
  name: str = Field(..., description='Defines the name of the geofence')
  color: str = Field(..., description='Defines the color of the geofence')

  geom_wgs84: dict[str, Any] = Field(description='GeoJSON geometry', default_factory=dict)
  geom_web_mercator: dict[str, Any] = Field(description='GeoJSON geometry in Web Mercator', default_factory=dict)

  owner_id: int | None = Field(default=None, description='Defines the owner ID of the geofence')
