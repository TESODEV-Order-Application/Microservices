from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class Address(BaseModel):
    addressLine: Optional[str]
    city: str
    country: str
    cityCode: int

class Product(BaseModel):
    id: UUID
    name: str
    imageUrl: str

class Order(BaseModel):
    id: UUID
    customerId: UUID
    quantity: int
    price: float
    status: str
    address: Address
    product: Product
    createdAt: datetime
    updatedAt: datetime

class UpdateOrder(BaseModel):
    customerId: UUID
    quantity: int
    price: float
    status: str
    product: Product