from pydantic import BaseModel, ConfigDict, Field, field_serializer

from .chart_data_serie_type import ChartDataSerieType
from .scatter_serie_item import ScatterSerieItem


class ScatterSerie(BaseModel):
  """Chart Data Serie for Timeline charts"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  data: list[ScatterSerieItem] = Field(description='List of data points', default_factory=list)
  color: str = Field(description='Color of the serie', default='')
  label: str = Field(description='Label of the serie', default='')
  serie_type: ChartDataSerieType = Field(description='Type of the serie', default=ChartDataSerieType.SCATTER)

  @field_serializer('serie_type', when_used='always')
  def serialize_serie_type(self, serie_type: ChartDataSerieType) -> str:
    return serie_type.value
