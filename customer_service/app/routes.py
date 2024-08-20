from fastapi import APIRouter, HTTPException
from uuid import UUID
from .models import Customer
from typing import List

from app.MongoDB import mongodb


router = APIRouter(prefix="/customer", tags=["Customer"])

# In-memory database substitute for demonstration purposes
customers_db = {} #############################


@router.get("/test")
async def test():
    return await mongodb.collections["customers"].find_one({}, {"_id": 0})



@router.post("/", response_model=UUID)
async def create(customer: Customer):
    customer.id = UUID() 
    customers_db[customer.id] = customer
    return customer.id

@router.put("/{customer_id}", response_model=bool)
async def update(customer_id: UUID, customer: Customer):
    if customer_id not in customers_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    customers_db[customer_id] = customer
    return True

@router.delete("/{customer_id}", response_model=bool)
async def delete(customer_id: UUID):
    if customer_id in customers_db:
        del customers_db[customer_id]
        return True
    raise HTTPException(status_code=404, detail="Customer not found")

@router.get("/", response_model=List[Customer])
async def getAll():
    return list(customers_db.values())

@router.get("/{customer_id}", response_model=Customer)
async def get(customer_id: UUID):
    if customer_id in customers_db:
        return customers_db[customer_id]
    raise HTTPException(status_code=404, detail="Customer not found")


@router.get("/validate/{customer_id}", response_model=bool)
async def validate(customer_id: UUID):
    return customer_id in customers_db