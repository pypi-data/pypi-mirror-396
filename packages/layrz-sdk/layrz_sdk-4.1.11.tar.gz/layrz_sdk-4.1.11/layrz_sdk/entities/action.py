from pydantic import BaseModel, ConfigDict, Field, field_serializer

from .action_geofence_ownership import ActionGeofenceOwnership
from .action_kind import ActionKind
from .action_subkind import ActionSubKind
from .geofence_category import GeofenceCategory


class Action(BaseModel):
  """Action entity"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    ...,
    description='Primary key of the action entity',
    alias='id',
  )
  name: str = Field(..., description='Name of the action')
  kind: ActionKind = Field(..., description='Kind of the action')

  @field_serializer('kind', when_used='always')
  def serialize_kind(self, kind: ActionKind) -> str:
    return kind.value

  command_id: int | None = Field(
    default=None,
    description='Tag ID associated with the action to send commands to primary devices',
  )

  subkind: ActionSubKind = Field(default=ActionSubKind.UNUSED, description='Subkind of the action')

  @field_serializer('subkind', when_used='always')
  def serialize_subkind(self, subkind: ActionSubKind) -> str:
    return subkind.value

  wait_for_image: bool = Field(
    default=False,
    description='Whether to wait for an image to be taken before executing the action',
    alias='watch_image',
  )

  geofence_cateogry: GeofenceCategory = Field(
    default=GeofenceCategory.NONE,
    description='Geofence category of the action',
  )

  @field_serializer('geofence_cateogry', when_used='always')
  def serialize_geofence_category(self, geofence_category: GeofenceCategory) -> str:
    return geofence_category.value

  geofence_name_formula: str | None = Field(
    default=None,
    description='Formula to generate the geofence name',
    alias='geofence_name',
  )

  geofence_radius: float | None = Field(
    default=None,
    description='Radius of the geofence in meters',
    alias='geofence_radius',
  )

  mappit_route_id: str | None = Field(
    default=None,
    description='Route ID for Mappit integration',
  )

  new_geofence_ownership: ActionGeofenceOwnership = Field(
    default=ActionGeofenceOwnership.NONE,
    description='Ownership of the new geofence created by the action',
  )

  @field_serializer('new_geofence_ownership', when_used='always')
  def serialize_new_geofence_ownership(self, ownership: ActionGeofenceOwnership) -> str:
    return ownership.value

  owner_id: int | None = Field(default=None, description='Owner ID')
