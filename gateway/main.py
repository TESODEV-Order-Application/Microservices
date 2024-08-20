from fastapi import FastAPI, Request, HTTPException, Response
from typing import Optional
import uvicorn
import httpx

app = FastAPI() 

# Define the base URLs for the microservices
services = {
    "customer": "8001",
    "order": "8002"
}

async def proxy_request(request: Request, service: str, path: str = "", body: dict = None):
    if service in services:
        url = f"http://193.164.4.17:{services[service]}/{service}/{path}"
    else:
        raise HTTPException(status_code=404, detail="Service not found")

    print(request.method.lower())

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=url,
            content=await request.body(),
            json=body
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )


@app.get("/{service}/{path:path}")
async def get(request: Request, service: str, path: Optional[str] = None):
    return await proxy_request(request, service, path)

@app.post("/{service}/{path:path}")
async def post(request: Request, service: str, path: str, body: dict):
    return await proxy_request(request, service, path, body)

@app.put("/{service}/{path:path}")
async def put(request: Request, service: str, path: str, body: dict):
    return await proxy_request(request, service, path, body)

@app.delete("/{service}/{path:path}")
async def delete(request: Request, service: str, path: str):
    return await proxy_request(request, service, path)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)