from datetime import timedelta

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class AssetConstants(BaseModel):
  """Asset constants"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )
  distance_traveled: float = Field(default=0.0, description='Total distance traveled by the asset in meters')
  primary_device: str = Field(default='N/A', description='Primary device associated with the asset')
  elapsed_time: timedelta = Field(
    default=timedelta(seconds=0),
    description='Total elapsed time for the asset in seconds',
  )

  @field_serializer('elapsed_time', when_used='always')
  def serialize_elapsed_time(self, elapsed_time: timedelta) -> float:
    return elapsed_time.total_seconds()
