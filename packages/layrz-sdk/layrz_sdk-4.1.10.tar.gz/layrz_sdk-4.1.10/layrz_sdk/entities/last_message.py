from pydantic import BaseModel, ConfigDict, Field

from .asset import Asset
from .message import Message


class LastMessage(Message, BaseModel):
  """LastMessage definition"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  asset: Asset = Field(description='Defines the asset of the last message')
