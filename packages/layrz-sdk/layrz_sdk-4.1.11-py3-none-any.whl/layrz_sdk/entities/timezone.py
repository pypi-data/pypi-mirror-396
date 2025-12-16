from pydantic import BaseModel, ConfigDict, Field


class Timezone(BaseModel):
  """Timezone entity"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    ...,
    description='Defines the primary key of the timezone',
    alias='id',
  )
  name: str = Field(..., description='Defines the name of the timezone')
  offset: int = Field(..., description='Defines the offset of the timezone in seconds from UTC')
