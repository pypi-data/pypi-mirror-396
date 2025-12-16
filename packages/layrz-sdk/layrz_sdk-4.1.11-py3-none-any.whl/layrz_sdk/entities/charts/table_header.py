from pydantic import BaseModel, ConfigDict, Field


class TableHeader(BaseModel):
  """Table header chart configuration"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  label: str = Field(description='Label of the header')
  key: str = Field(description='Key of the header')
