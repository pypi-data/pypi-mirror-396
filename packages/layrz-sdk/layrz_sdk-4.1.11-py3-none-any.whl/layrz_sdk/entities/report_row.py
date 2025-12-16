from pydantic import BaseModel, ConfigDict, Field

from .report_col import ReportCol


class ReportRow(BaseModel):
  """Report row definition"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  content: list[ReportCol] = Field(description='List of report columns', default_factory=list)
  compact: bool = Field(description='Compact mode', default=False)
