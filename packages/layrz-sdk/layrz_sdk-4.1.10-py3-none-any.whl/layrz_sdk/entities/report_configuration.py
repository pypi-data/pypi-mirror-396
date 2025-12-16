from pydantic import BaseModel, ConfigDict, Field


class ReportConfiguration(BaseModel):
  """Report configuration entity"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  title: str = Field(description='Report title')
  pages_count: int = Field(description='Number of pages in the report')
