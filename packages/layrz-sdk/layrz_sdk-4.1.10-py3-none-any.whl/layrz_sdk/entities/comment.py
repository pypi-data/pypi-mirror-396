from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from .user import User


class Comment(BaseModel):
  """Comment entity"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    description='Comment ID',
    alias='id',
  )
  content: str = Field(description='Comment content')
  user: User | None = Field(description='Operator/User what commented the case. None if system generated')
  submitted_at: datetime = Field(description='Date of comment submission')

  @field_serializer('submitted_at', when_used='always')
  def serialize_submitted_at(self, submitted_at: datetime) -> float:
    return submitted_at.timestamp()

  metadata: dict[str, Any] = Field(
    default_factory=dict,
    description='Additional metadata associated with the comment',
  )
