from pydantic import BaseModel, ConfigDict, Field


class AssetContact(BaseModel):
  """Asset contact information"""

  model_config = ConfigDict(
    validate_by_name=False,
    validate_by_alias=True,
    serialize_by_alias=True,
  )

  name: str = Field(default='', description='Name of the contact person for the asset')
  phone: str = Field(default='', description='Phone number of the contact person for the asset')
  email: str = Field(default='', description='Email address of the contact person for the asset')
