from pydantic import BaseModel, ConfigDict, Field

from .sensor_mask import SensorMask


class Sensor(BaseModel):
  """Sensor entity"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    description='Defines the primary key of the sensor',
    alias='id',
  )
  name: str = Field(description='Defines the name of the sensor')
  slug: str = Field(description='Defines the slug of the sensor')
  formula: str = Field(
    default='',
    description='Defines the formula of the sensor, used for calculations',
  )
  mask: list[SensorMask] | None = Field(
    default=None,
    description='Defines the mask of the sensor, used for filtering data',
  )

  measuring_unit: str | None = Field(
    default=None,
    description='Defines the measuring unit of the sensor, e.g., km/h, °C',
  )
