"""Entry entity"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from .ats_purchaseorder import AtsPurchaseOrder, DeliveryCategories, OrderCategories, OrderStatus


class AtsOperationMovement(BaseModel):
  """Ats operation movement entity"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int | None = Field(
    description='Defines the primary key of the Function',
    default=None,
    alias='id',
  )
  status: OrderStatus | None = Field(description='Current status of the order', default=None)

  @field_serializer('status', when_used='always')
  def serialize_status(self, status: OrderStatus | None) -> str | None:
    return status.value if status else None

  created_at: datetime | None = Field(description='Timestamp when the operation movement was created', default=None)

  @field_serializer('created_at', when_used='always')
  def serialize_created_at(self, created_at: datetime | None) -> float | None:
    return created_at.timestamp() if created_at else None

  asset_id: int | None = Field(description='ID of the asset', default=None)
  operation_id: int | None = Field(description='ID of the operation', default=None)


class AtsOperation(BaseModel):
  """Entry entity"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  pk: int = Field(
    description='Defines the primary key of the Function',
    alias='id',
  )
  purchased_at: datetime = Field(description='Timestamp when the operation was purchased')

  @field_serializer('purchased_at', when_used='always')
  def serialize_purchased_at(self, purchased_at: datetime) -> float:
    return purchased_at.timestamp()

  order_status: OrderStatus = Field(..., description='Current status of the order')

  @field_serializer('order_status', when_used='always')
  def serialize_order_status(self, order_status: OrderStatus) -> str:
    return order_status.value

  category: OrderCategories = Field(..., description='Category of the operation')

  @field_serializer('category', when_used='always')
  def serialize_category(self, category: OrderCategories) -> str:
    return category.value

  deliver_category: DeliveryCategories = Field(..., description='Delivery category of the operation')

  @field_serializer('deliver_category', when_used='always')
  def serialize_deliver_category(self, deliver_category: DeliveryCategories) -> str:
    return deliver_category.value

  seller_asset_id: int = Field(description='ID of the seller asset')
  transport_asset_id: int = Field(description='ID of the transport asset')
  finished_at: datetime | None = Field(description='Timestamp when the operation was finished', default=None)

  @field_serializer('finished_at', when_used='always')
  def serialize_finished_at(self, finished_at: datetime | None) -> float | None:
    return finished_at.timestamp() if finished_at else None

  history: list[AtsOperationMovement] = Field(description='List of operation movements')
  purchase_orders: list[AtsPurchaseOrder] = Field(description='List of purchase orders')
