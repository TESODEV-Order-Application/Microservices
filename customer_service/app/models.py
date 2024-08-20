from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

class Address(BaseModel):
    addressLine: Optional[str]
    city: str
    country: str
    cityCode: int

class Customer(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    address: Address
    createdAt: datetime
    updatedAt: datetime

class UpdateCustomer(BaseModel):
    name: str
    email: EmailStr
    address: Address