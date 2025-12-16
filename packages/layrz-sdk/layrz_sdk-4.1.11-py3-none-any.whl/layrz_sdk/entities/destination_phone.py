from typing import Self

from pydantic import BaseModel, ConfigDict, Field


class DestinationPhone(BaseModel):
  """Destination Phone"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  phone_number: str = Field(
    ...,
    description='Defines the phone number for Twilio notifications',
    alias='phoneNumber',
  )

  country_code: str = Field(
    ...,
    description='Defines the country code for the phone number',
    alias='countryCode',
  )

  @property
  def formatted_phone_number(self: Self) -> str:
    """Returns the formatted phone number"""
    return f'{self.country_code}{self.phone_number}'
