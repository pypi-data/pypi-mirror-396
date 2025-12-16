from pydantic import BaseModel, ConfigDict, Field


class StaticPosition(BaseModel):
  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )
  latitude: float = Field(
    ...,
    description='Latitude of the static position',
  )
  longitude: float = Field(
    ...,
    description='Longitude of the static position',
  )

  altitude: float | None = Field(
    default=None,
    description='Altitude of the static position',
  )
