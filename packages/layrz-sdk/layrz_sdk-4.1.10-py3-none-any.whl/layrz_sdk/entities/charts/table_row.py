from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TableRow(BaseModel):
  """Table row chart configuration"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  data: Any = Field(description='Data of the row')
