from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class Preset(BaseModel):
  """Preset entity"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    description='Defines the primary key of the preset',
    alias='id',
  )
  name: str = Field(description='Defines the name of the preset')
  valid_before: datetime = Field(
    ...,
    description='Defines the date and time before which the preset is valid',
  )

  @field_serializer('valid_before', when_used='always')
  def serialize_valid_before(self, valid_before: datetime) -> float:
    return valid_before.timestamp()

  comment: str = Field(
    default='',
    description='Defines the comment of the preset',
  )
  owner_id: int = Field(
    ...,
    description='Defines the ID of the owner of the preset',
  )
