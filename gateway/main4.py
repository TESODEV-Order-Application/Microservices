from fastapi import FastAPI, Request, HTTPException, Response
import uvicorn
import httpx
import os

app = FastAPI()


ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL')
CUSTOMER_SERVICE_URL = os.getenv('CUSTOMER_SERVICE_URL')

async def proxy_request(request: Request, full_path: str, method: str, body: dict = None):
    if full_path.startswith("order"):
        url = f"{ORDER_SERVICE_URL}/{full_path}"
    elif full_path.startswith("customer"):
        url = f"{CUSTOMER_SERVICE_URL}/{full_path}"
    else:
        raise HTTPException(status_code=404, detail="Service not found")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=request.headers.raw,
                content=await request.body(),
                json=body,
                timeout=None
            )

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(exc)}")


@app.api_route("/{full_path:path}", methods=["GET"])
async def get(full_path: str, request: Request):
    return await proxy_request(request, full_path, "get")

@app.api_route("/{full_path:path}", methods=["POST"])
async def post(full_path: str, request: Request, body: dict):
    return await proxy_request(request, full_path, "post", body)

@app.api_route("/{full_path:path}", methods=["PUT"])
async def put(full_path: str, request: Request, body: dict):
    return await proxy_request(request, full_path, "put", body)

@app.api_route("/{full_path:path}", methods=["DELETE"])
async def delete(full_path: str, request: Request):
    return await proxy_request(request, full_path, "delete")



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080) 