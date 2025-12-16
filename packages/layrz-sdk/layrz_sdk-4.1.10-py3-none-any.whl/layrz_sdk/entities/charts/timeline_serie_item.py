from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TimelineSerieItem(BaseModel):
  """Chart Data Serie Item for Timeline Charts"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  name: str = Field(description='Name of the item')
  start_at: datetime = Field(description='Start date of the item')
  end_at: datetime = Field(description='End date of the item')
  color: str = Field(description='Color of the item')
