from pydantic import BaseModel, ConfigDict, Field


class ScatterSerieItem(BaseModel):
  """Chart Data Serie Item for Scatter Charts"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  x: float = Field(description='X value of the item')
  y: float = Field(description='Y value of the item')
