from pydantic import BaseModel, ConfigDict, Field

from .timeline_serie_item import TimelineSerieItem


class TimelineSerie(BaseModel):
  """Chart Data Serie for Timeline charts"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  data: list[TimelineSerieItem] = Field(description='List of data points', default_factory=list)
  label: str = Field(description='Label of the serie')
