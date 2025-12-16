from datetime import datetime
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from .case_ignored_status import CaseIgnoredStatus
from .case_status import CaseStatus
from .comment import Comment
from .trigger import Trigger


class Case(BaseModel):
  """Case entity"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    description='Defines the primary key of the case',
    alias='id',
  )
  trigger: Trigger = Field(description='Defines the trigger of the case')
  asset_id: int = Field(description='Defines the asset ID of the case')
  comments: list[Comment] = Field(default_factory=list, description='Defines the comments of the case')
  opened_at: datetime = Field(description='Defines the date when the case was opened')

  @field_serializer('opened_at', when_used='always')
  def serialize_opened_at(self, opened_at: datetime) -> float:
    return opened_at.timestamp()

  closed_at: datetime | None = Field(default=None, description='Defines the date when the case was closed')

  @field_serializer('closed_at', when_used='always')
  def serialize_closed_at(self, closed_at: datetime | None) -> float | None:
    return closed_at.timestamp() if closed_at else None

  status: CaseStatus = Field(description='Defines the status of the case', default=CaseStatus.CLOSED)

  @field_serializer('status', when_used='always')
  def serialize_status(self, status: CaseStatus) -> str:
    return status.value

  ignored_status: CaseIgnoredStatus = Field(
    description='Defines the ignored status of the case',
    default=CaseIgnoredStatus.NORMAL,
  )

  @field_serializer('ignored_status', when_used='always')
  def serialize_ignored_status(self, ignored_status: CaseIgnoredStatus) -> str:
    return ignored_status.value

  sequence: int | str | None = Field(
    default=None,
    description='Defines the sequence of the case. This is a unique identifier for the case',
  )

  stack_count: int = Field(
    default=1,
    description='Defines how many cases are stacked together. Only applicable if the trigger allows stacking',
  )

  @model_validator(mode='before')
  def _validate_model(cls: Self, data: dict[str, Any]) -> dict[str, Any]:
    """Validate model"""
    sequence = data.get('sequence')
    if sequence is not None and isinstance(sequence, int):
      trigger = data['trigger']
      if not isinstance(trigger, Trigger):
        if pk := data.get('pk'):
          data['sequence'] = f'{trigger["code"]}/{pk}'
        elif id_ := data.get('id'):
          data['sequence'] = f'{trigger["code"]}/{id_}'
        else:
          data['sequence'] = f'{trigger["code"]}/{sequence}'
      else:
        data['sequence'] = f'{trigger.code}/{sequence}'
    else:
      data['sequence'] = f'GENERIC/{data["pk"]}'

    if stack_count := data.get('stack_count'):
      if not isinstance(stack_count, int) or stack_count < 1:
        data['stack_count'] = 1
    else:
      data['stack_count'] = 1

    return data
