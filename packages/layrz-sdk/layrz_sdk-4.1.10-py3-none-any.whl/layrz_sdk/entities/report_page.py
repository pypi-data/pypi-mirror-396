from pydantic import BaseModel, ConfigDict, Field

from .report_header import ReportHeader
from .report_row import ReportRow


class ReportPage(BaseModel):
  """Report page definition"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  name: str = Field(description='Name of the page. Length should be less than 60 characters')
  headers: list[ReportHeader] = Field(description='List of report headers', default_factory=list)
  rows: list[ReportRow] = Field(description='List of report rows', default_factory=list)
  freeze_header: bool = Field(description='Freeze header', default=False)
