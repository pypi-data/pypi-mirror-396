import warnings
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from .text_alignment import TextAlignment


class ReportHeader(BaseModel):
  """Report header entity"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  content: Any = Field(description='Header content')
  color: str = Field(description='Header color', default='#ffffff')
  align: TextAlignment = Field(description='Header text alignment', default=TextAlignment.CENTER)

  @field_serializer('align', when_used='always')
  def serialize_align(self, align: TextAlignment) -> str:
    return align.value

  bold: bool = Field(description='Bold text', default=False)
