from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
  """User entity"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    description='Defines the primary key of the user',
    alias='id',
  )
  name: str = Field(description='Defines the name of the user')
