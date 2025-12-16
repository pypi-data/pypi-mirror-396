"""Trigger entity"""

from datetime import time, timedelta
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from .trigger_kind import TriggerCaseKind, TriggerCommentPattern, TriggerGeofenceKind, TriggerKind
from .weekday import Weekday


class Trigger(BaseModel):
  """Trigger entity"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    description='Defines the primary key of the trigger',
    alias='id',
  )
  name: str = Field(description='Defines the name of the trigger')
  code: str = Field(description='Defines the code of the trigger')

  cooldown_time: timedelta = Field(
    default_factory=lambda: timedelta(seconds=0),
    description='Defines the cooldown time of the trigger',
  )

  @field_serializer('cooldown_time', when_used='always')
  def serialize_cooldown_time(self, value: timedelta) -> float:
    """Serialize cooldown_time to total seconds."""
    return value.total_seconds()

  type_: TriggerKind | None = Field(
    default=None,
    description='Defines the kind of the trigger',
    alias='type',
  )

  @field_serializer('type_', when_used='always')
  def serialize_type(self, value: TriggerKind | None) -> str | None:
    return value.value if value else None

  presence_type: TriggerGeofenceKind | None = Field(
    default=None,
    description='Defines the geofence kind of the trigger',
  )

  @field_serializer('presence_type', when_used='always')
  def serialize_presence_type(self, value: TriggerGeofenceKind | None) -> str | None:
    return value.value if value else None

  case_type: TriggerCaseKind | None = Field(
    default=None,
    description='Defines the case kind of the trigger',
  )

  @field_serializer('case_type', when_used='always')
  def serialize_case_type(self, value: TriggerCaseKind | None) -> str | None:
    return value.value if value else None

  case_comment_pattern: TriggerCommentPattern | None = Field(
    default=None,
    description='Defines the comment pattern of the trigger',
  )

  @field_serializer('case_comment_pattern', when_used='always')
  def serialize_case_comment_pattern(self, value: TriggerCommentPattern | None) -> str | None:
    return value.value if value else None

  case_comment_value: str | None = Field(
    default=None,
    description='Defines the comment pattern value of the trigger',
  )

  exact_hour: time | None = Field(
    default=None,
    description='Defines the exact hour of the trigger',
  )
  crontab_format: str | None = Field(
    default=None,
    description='Defines the crontab format of the trigger',
  )

  weekdays: list[Weekday] = Field(
    default_factory=list,
    description='Defines the weekdays of the trigger',
  )

  @field_serializer('weekdays', when_used='always')
  def serialize_weekdays(self, value: list[Weekday]) -> list[str]:
    return [day.value for day in value]

  is_plain_crontab: bool = Field(
    default=False,
    description='Defines if the trigger is a plain crontab',
  )

  timezone_id: int | None = Field(
    default=None,
    description='Defines the timezone ID of the trigger',
  )

  parameters: list[str] = Field(
    default_factory=list,
    description='Defines the parameters of the trigger',
  )

  manual_action_fields: list[dict[str, Any]] = Field(
    default_factory=list,
    description='Defines the fields for manual action in the trigger',
  )

  @field_validator('manual_action_fields', mode='before')
  def validate_manual_action_fields(cls, value: Any) -> list[dict[str, Any]]:
    return value if isinstance(value, list) else []

  formula: str | None = Field(
    default=None,
    description='Defines the formula of the trigger, this formula is only LCL (Layrz Computation Language) compatible',
  )

  script: str | None = Field(
    default=None,
    description='Defines the script of the trigger, depending of the trigger kidn, this script can be in Python, '
    + 'Javascript, Lua, Dart or Golang. (Or any other language supported by the SDK)',
  )

  is_legacy: bool = Field(
    default=False,
    description='Defines if the trigger is legacy, normally when a version of the trigger is not compatible '
    + 'with the current version of the SDK',
  )

  priority: int = Field(
    default=0,
    description='Defines the priority of the trigger',
  )

  @field_validator('priority', mode='before')
  def validate_priority(cls, value: Any) -> int:
    """Ensure priority is an integer."""
    if isinstance(value, int):
      return value
    try:
      return int(value)
    except (ValueError, TypeError):
      return 0

  color: str | None = Field(
    default='#2196F3',
    description='Defines the color of the trigger',
  )

  sequence: int = Field(
    default=0,
    description='Defines the sequence of the trigger',
  )

  care_protocol_id: int | None = Field(
    default=None,
    description='Defines the care protocol ID of the trigger',
  )
  has_case_expirity: bool = Field(
    default=False,
    description='Defines if the trigger has case expiry',
  )

  when_case_expires_delta: timedelta | None = Field(
    default=None,
    description='Defines when the trigger expires delta',
  )

  @field_serializer('when_case_expires_delta', when_used='always')
  def serialize_when_case_expires_delta(self, value: timedelta | None) -> float | None:
    return value.total_seconds() if value else None

  should_stack: bool = Field(
    default=False,
    description='Defines if the trigger cases should stack',
  )
  stack_upper_limit: int | None = Field(
    default=None,
    description='Defines the stack upper limit of the trigger cases. None means no limit',
  )

  owner_id: int | None = Field(
    default=None,
    description='Owner ID',
  )

  search_time_delta: timedelta | None = Field(
    default=None,
    description='Defines the search time delta of the trigger',
  )

  @field_serializer('search_time_delta', when_used='always')
  def serialize_search_time_delta(self, value: timedelta | None) -> float | None:
    return value.total_seconds() if value else None

  is_paused: bool = Field(
    default=False,
    description='Defines if the trigger is paused',
  )

  should_generate_locator: bool = Field(
    default=False,
    description='Defines if the trigger should generate a locator',
  )

  locator_expires_delta: timedelta | None = Field(
    default=None,
    description='Defines the locator expires delta of the trigger',
  )

  @field_serializer('locator_expires_delta', when_used='always')
  def serialize_locator_expires_delta(self, value: timedelta | None) -> float | None:
    return value.total_seconds() if value else None

  locator_expires_triggers_ids: list[int] = Field(
    default_factory=list,
    description='Defines the locator expires triggers IDs of the trigger',
  )

  locator_geofences_ids: list[int] = Field(
    default_factory=list,
    description='Defines the locator geofences IDs of the trigger',
  )

  locator_customization_id: int | None = Field(
    default=None,
    description='Defines the locator customization ID of the trigger',
  )
