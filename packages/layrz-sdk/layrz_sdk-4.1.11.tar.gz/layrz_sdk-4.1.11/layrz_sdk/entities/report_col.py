import warnings
from typing import Any, Optional, Self

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from .report_data_type import ReportDataType
from .text_alignment import TextAlignment


class ReportCol(BaseModel):
  """Report column entity"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  content: Any = Field(description='Column content')
  color: str = Field(description='Column color', default='#ffffff')
  text_color: Optional[str] = Field(description='Column text color', default=None)
  align: TextAlignment = Field(description='Column text alignment', default=TextAlignment.LEFT)

  @field_serializer('align', when_used='always')
  def serialize_align(self, align: TextAlignment) -> str:
    return align.value

  data_type: ReportDataType = Field(description='Column data type', default=ReportDataType.STR)

  @field_serializer('data_type', when_used='always')
  def serialize_data_type(self, data_type: ReportDataType) -> str:
    return data_type.value

  datetime_format: str = Field(description='Datetime format', default='%Y-%m-%d %H:%M:%S')
  currency_symbol: str = Field(description='Currency symbol', default='')
  bold: bool = Field(description='Bold text', default=False)
  lock: bool = Field(description='Lock column', default=False)

  @field_validator('text_color', mode='before')
  def _validate_text_color(cls: Self, value: Any) -> Any:
    """Validate text color"""
    if value is not None:
      warnings.warn(
        'text_color is deprecated, the algorithm will calculate the rigth text color instead',
        DeprecationWarning,
        stacklevel=2,
      )

    return value
