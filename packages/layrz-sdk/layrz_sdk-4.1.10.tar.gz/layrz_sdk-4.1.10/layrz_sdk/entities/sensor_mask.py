from pydantic import BaseModel, ConfigDict, Field


class SensorMask(BaseModel):
  """Sensor entity"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  icon: str | None = Field(
    default=None,
    description='Defines the icon of the sensor',
  )
  text: str | None = Field(
    default=None,
    description='Defines the text of the sensor',
  )
  color: str | None = Field(
    default=None,
    description='Defines the color of the sensor, used for visual representation',
  )
  value: str | float | int | None = Field(
    default=None,
    description='Defines the value of the sensor, can be of various types',
  )
