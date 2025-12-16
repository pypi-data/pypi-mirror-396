from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from .asset import Asset


class OrderStatus(StrEnum):
  GENERATED = 'GENERATED'
  IN_TRANSIT = 'IN_TRANSIT'
  WAITING_TO_DISPATCH = 'WAITING_TO_DISPATCH'  # For trucks
  DELIVERED = 'DELIVERED'
  # For the purchase order status in the port
  READY_TO_OPERATE = 'READY_TO_OPERATE'
  UNLOADING_OPERATION = 'UNLOADING_OPERATION'
  UNLOADING_FUEL = 'UNLOADING_FUEL'
  UNLOADING_FUEL_INTERRUPTED = 'UNLOADING_FUEL_INTERRUPTED'
  DESTINATION_BERTH_EXIT = 'DESTINATION_BERTH_EXIT'
  ORIGIN_BERTH_EXIT = 'ORIGIN_BERTH_EXIT'


class OrderCategories(StrEnum):
  PICKUP = 'PICKUP'
  PICKUP_TO_SUPPLIER = 'PICKUP_TO_SUPPLIER'
  TRANSFER = 'TRANSFER'
  DELIVERY_TO_SUPPLIER = 'DELIVERY_TO_SUPPLIER'
  DELIVERY_TO_RESELLER = 'DELIVERY_TO_RESELLER'
  FOR_SALE_OUTSIDE = 'FOR_SALE_OUTSIDE'
  DELIVERY_TO_STORAGE = 'DELIVERY_TO_STORAGE'
  RETURN_FROM_STORAGE = 'RETURN_FROM_STORAGE'
  NOT_DEFINED = 'NOT_DEFINED'


class DeliveryCategories(StrEnum):
  SAME_STATE = 'SAME_STATE'
  OTHER_STATE = 'OTHER_STATE'
  NOT_DEFINED = 'NOT_DEFINED'


class AtsPurchaseOrder(BaseModel):
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

  order_id: int = Field(description='ID of the order')
  category: OrderCategories | None = Field(description='Category of the operation', default=None)

  @field_serializer('category', when_used='always')
  def serialize_category(self, category: OrderCategories | None) -> str | None:
    return category.value if category else None

  deliver_category: DeliveryCategories | None = Field(description='Delivery category of the operation', default=None)

  @field_serializer('deliver_category', when_used='always')
  def serialize_deliver_category(self, deliver_category: DeliveryCategories | None) -> str | None:
    return deliver_category.value if deliver_category else None

  seller_asset_id: int = Field(description='ID of the seller asset')
  transport_asset_id: int | None = Field(description='ID of the transport asset', default=None)
  asset_id: int = Field(description='ID of the asset')

  seller_asset: Asset | None = Field(description='Seller asset details', default=None)
  transport_asset: Asset | None = Field(description='Transport asset details', default=None)
  asset: Asset | None = Field(description='Destination asset details', default=None)
  delivered_at: datetime | None = Field(description='Timestamp when the operation was delivered', default=None)

  @field_serializer('delivered_at', when_used='always')
  def serialize_delivered_at(self, delivered_at: datetime | None) -> float | None:
    return delivered_at.timestamp() if delivered_at else None

  eta: datetime | None = Field(description='Estimated time of arrival to the destination', default=None)

  @field_serializer('eta', when_used='always')
  def serialize_eta(self, eta: datetime | None) -> float | None:
    return eta.timestamp() if eta else None

  eta_updated_at: datetime | None = Field(description='Timestamp when the ETA was last updated', default=None)

  @field_serializer('eta_updated_at', when_used='always')
  def serialize_eta_updated_at(self, eta_updated_at: datetime | None) -> float | None:
    return eta_updated_at.timestamp() if eta_updated_at else None

  invoice_type: str = Field(description='Type of the invoice')
  operation_id: int | None = Field(description='ID of the operation', default=None)
  products_information: list[dict[str, Any]] = Field(description='List of products information', default_factory=list)
