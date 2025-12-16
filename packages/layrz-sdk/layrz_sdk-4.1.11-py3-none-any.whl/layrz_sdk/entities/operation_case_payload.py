from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from layrz_sdk.constants import UTC
from layrz_sdk.entities.trigger import Trigger


class OperationCaseCommentPayload(BaseModel):
  """Operation case comment payload entity"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    ...,
    description='Defines the primary key of the operation case comment',
    alias='id',
  )
  user: str = Field(..., description='Defines the user who created the operation case comment')
  content: str = Field(..., description='Defines the content of the operation case comment')
  created_at: datetime = Field(
    default_factory=lambda: datetime.now(UTC),
    description='Defines the creation date of the operation case comment',
  )

  @field_serializer('created_at', when_used='always')
  def serialize_created_at(self, created_at: datetime) -> float:
    return created_at.timestamp()


class OperationCasePayload(BaseModel):
  """Operation case payload entity"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    description='Defines the primary key of the operation case payload',
    alias='id',
  )
  created_at: datetime = Field(
    default_factory=lambda: datetime.now(UTC),
    description='Defines the creation date of the operation case payload',
  )

  @field_serializer('created_at', when_used='always')
  def serialize_created_at(self, created_at: datetime) -> float:
    return created_at.timestamp()

  updated_at: datetime = Field(
    default_factory=lambda: datetime.now(UTC),
    description='Defines the last update date of the operation case payload',
  )

  @field_serializer('updated_at', when_used='always')
  def serialize_updated_at(self, updated_at: datetime) -> float:
    return updated_at.timestamp()

  trigger: Trigger = Field(
    ...,
    description='Defines the trigger associated with the operation case payload',
  )

  @field_validator('trigger', mode='before')
  def serialize_trigger(cls, value: Any) -> Trigger:
    """Serialize trigger to a dictionary"""
    if isinstance(value, Trigger):
      return Trigger(
        id=value.pk,  # ty: ignore
        name=value.name,
        code=value.code,
      )
    if isinstance(value, dict):
      return Trigger.model_validate(value)

    raise ValueError('Trigger must be an instance of Trigger or a dictionary')

  file_id: int | None = Field(
    default=None,
    description='Defines the file ID associated with the operation case payload',
  )

  file_created_at: datetime | None = Field(
    default=None,
    description='Defines the creation date of the file associated with the operation case payload',
  )

  @field_serializer('file_created_at', when_used='always')
  def serialize_file_created_at(self, file_created_at: datetime | None) -> float | None:
    return file_created_at.timestamp() if file_created_at else None

  comment: OperationCaseCommentPayload | None = Field(
    default=None,
    description='Defines the comment associated with the operation case payload',
  )
