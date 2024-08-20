from fastapi import APIRouter, HTTPException
from typing import List
from bson import Binary
from uuid import UUID, uuid4
from datetime import datetime

from app.MongoDB import mongodb
from .models import Order, UpdateOrder

router = APIRouter(prefix="/order", tags=["Order"])


@router.post("/", response_model=UUID)
async def create(order: UpdateOrder):
    response = await mongodb.collections["customers"].find_one({"id": Binary.from_uuid(order.customerId)}, {"address": 1})
    if response is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    order = order.dict()
    order = Order(**order |
            {
                "id": uuid4(),
                "address": response["address"],
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
        )

    order.id = Binary.from_uuid(order.id) 
    order.customerId = Binary.from_uuid(order.customerId)
    order.product.id = Binary.from_uuid(order.product.id)
    
    await mongodb.collections["orders"].insert_one(order.dict())
    return order.id

########################################################
@router.put("/{orderId}", response_model=bool)
async def update(orderId: UUID, order: UpdateOrder):
    orderId = Binary.from_uuid(orderId)

    order = order.dict()
    order["updatedAt"] = datetime.utcnow()

    return (await mongodb.collections["orders"].update_one({"id": orderId}, {"$set": order}, upsert=False)).matched_count > 0
########################################################

@router.delete("/{orderId}", response_model=bool)
async def delete(orderId: UUID): #OTHER RELATİON LOGİC
    orderId = Binary.from_uuid(orderId)
    return (await mongodb.collections["orders"].delete_one({"id": orderId})).deleted_count > 0


@router.get("/", response_model=List[Order])
async def getAll():
    return await mongodb.collections["orders"].find({}, {"_id": 0}).to_list(length=None)


############################################
"""
@router.get("/{customerId}", response_model=List[Order])
async def get(customerId: UUID):
    if customerId in orders_db: #######
        return orders_db[customerId]
    raise HTTPException(status_code=404, detail="Order not found")
"""
############################################


@router.get("/{orderId}", response_model=Order)
async def get(orderId: UUID):
    orderId = Binary.from_uuid(orderId)

    response = await mongodb.collections["orders"].find_one({"id": orderId}, {"_id": 0})
    if response is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return response


@router.put("/changeStatus/{orderId}", response_model=bool)
async def changeStatus(orderId: UUID, status: str):
    orderId = Binary.from_uuid(orderId)

    return (await mongodb.collections["orders"].update_one({"id": orderId}, {"$set": {"status": status}}, upsert=False)).matched_count > 0