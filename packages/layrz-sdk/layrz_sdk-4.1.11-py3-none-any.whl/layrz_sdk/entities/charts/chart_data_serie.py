"""Chart Data Serie"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from .chart_data_serie_type import ChartDataSerieType
from .chart_data_type import ChartDataType


class ChartDataSerie(BaseModel):
  """Chart Serie"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  data: Any = Field(description='Data of the serie')
  color: str = Field(description='Color of the serie', default='#000000')
  label: str = Field(description='Label of the serie', default='')
  serie_type: ChartDataSerieType = Field(description='Type of the serie', default=ChartDataSerieType.LINE)

  @field_serializer('serie_type', when_used='always')
  def serialize_serie_type(self, serie_type: ChartDataSerieType) -> str:
    return serie_type.value

  data_type: ChartDataType = Field(description='Type of the data', default=ChartDataType.NUMBER)

  @field_serializer('data_type', when_used='always')
  def serialize_data_type(self, data_type: ChartDataType) -> str:
    return data_type.value

  dashed: bool = Field(description='If the serie should be dashed', default=False)
