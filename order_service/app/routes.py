from fastapi import APIRouter, HTTPException
from uuid import UUID
from .models import Order
from typing import List

router = APIRouter(prefix="/order", tags=["Order"])

# In-memory database substitute for demonstration purposes
orders_db = {}

@router.post("/", response_model=UUID)
async def create(order: Order):
    order.id = UUID()
    orders_db[order.id] = order
    return order.id

@router.put("/{order_id}", response_model=bool)
async def update(order_id: UUID, order: Order):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    orders_db[order_id] = order
    return True

@router.delete("/{order_id}", response_model=bool)
async def delete(order_id: UUID):
    if order_id in orders_db:
        del orders_db[order_id]
        return True
    raise HTTPException(status_code=404, detail="Order not found")

@router.get("/", response_model=List[Order])
async def getAll():
    return list(orders_db.values())

############################################
@router.get("/{customerId}", response_model=List[Order])
async def get(customerId: UUID):
    if customerId in orders_db: #######
        return orders_db[customerId]
    raise HTTPException(status_code=404, detail="Order not found")
############################################

@router.get("/{order_id}", response_model=Order)
async def get(order_id: UUID):
    if order_id in orders_db:
        return orders_db[order_id]
    raise HTTPException(status_code=404, detail="Order not found")

@router.put("/changeStatus/{order_id}", response_model=bool)
async def changeStatus(order_id: UUID, status: str):
    if order_id in orders_db:
        order = orders_db[order_id]
        order.status = status
        orders_db[order_id] = order
        return True
    raise HTTPException(status_code=404, detail="Order not found")