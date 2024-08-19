from fastapi import FastAPI
import httpx

app = FastAPI()


@app.get("/customers/{customerId}")
async def getCustomer(customerId: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://customer_service:8000/customers/{customerId}")
    return response.json()

@app.get("/orders/{orderId}")
async def getOrder(orderId: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://order_service:8001/orders/{orderId}")
    return response.json()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)