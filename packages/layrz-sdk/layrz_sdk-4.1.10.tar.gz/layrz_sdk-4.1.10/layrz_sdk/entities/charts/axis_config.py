from pydantic import BaseModel, ConfigDict, Field, field_serializer

from .chart_data_type import ChartDataType


class AxisConfig(BaseModel):
  """Axis configuration"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  label: str = Field(default='', description='Label of the axis')
  measure_unit: str = Field(default='', description='Measure unit of the axis')
  min_value: float | None = Field(default=None, description='Minimum value of the axis')
  max_value: float | None = Field(default=None, description='Maximum value of the axis')
  data_type: ChartDataType = Field(default=ChartDataType.DATETIME, description='Data type of the axis')

  @field_serializer('data_type', when_used='always')
  def serialize_data_type(self, data_type: ChartDataType) -> str:
    return data_type.value
