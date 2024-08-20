from fastapi import APIRouter, HTTPException
from uuid import UUID, uuid4
from typing import List
from bson import Binary
from datetime import datetime

from app.MongoDB import mongodb
from .models import Customer, UpdateCustomer

router = APIRouter(prefix="/customer", tags=["Customer"])


@router.post("/", response_model=UUID)
async def create(customer: UpdateCustomer):
    customer = customer.dict()
    customer = Customer(**customer |
            {
                "id": Binary.from_uuid(uuid4()),
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
        )

    customer.id = Binary.from_uuid(uuid4()) 
    
    await mongodb.collections["customers"].insert_one(customer.dict())
    return customer.id


@router.put("/{customer_id}", response_model=bool)
async def update(customerId: UUID, customer: UpdateCustomer):
    customerId = Binary.from_uuid(customerId)

    customer = customer.dict()
    customer["updatedAt"] = datetime.utcnow()

    return (await mongodb.collections["customers"].update_one({"id": customerId}, {"$set": customer}, upsert=False)).matched_count > 0


@router.delete("/{customer_id}", response_model=bool)
async def delete(customerId: UUID): #OTHER RELATİON LOGİC
    customerId = Binary.from_uuid(customerId)
    return (await mongodb.collections["customers"].delete_one({"id": customerId})).deleted_count > 0


@router.get("/", response_model=List[Customer])
async def getAll():
    return await mongodb.collections["customers"].find({}, {"_id": 0}).to_list(length=None)


@router.get("/{customer_id}", response_model=Customer)
async def get(customerId: UUID):
    customerId = Binary.from_uuid(customerId)

    response = await mongodb.collections["customers"].find_one({"id": customerId}, {"_id": 0})
    if response is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return response


@router.get("/validate/{customer_id}", response_model=bool)
async def validate(customerId: UUID):
    customerId = Binary.from_uuid(customerId)

    return (await mongodb.collections["customers"].find_one({"id": customerId}, {"_id": 0})) != None