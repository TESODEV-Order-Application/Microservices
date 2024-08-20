from fastapi import FastAPI, Request
import uvicorn
import httpx

app = FastAPI()

# Define the base URLs for the microservices
CUSTOMER_SERVICE_URL = "http://193.164.4.17:8001/customer"
ORDER_SERVICE_URL = "http://193.164.4.17:8002/order"

services = {
    "customer": "8001",
    "order": "8002"
}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request, service: str, path: str = ""):

    if service in services:
        url = f"http://193.164.4.17:{services[service]}/{service}/{path}"
    else:
        pass#raise HTTPException(status_code=404, detail="Service not found")
    
    """
    import requests
    response = requests.request(
            method=self.command,
            url=url,
            data=ownRequest.body,
            allow_redirects=False
        )
    """
    # Prepare the request to be forwarded
    method = request.method.lower()
    print(method)
    async with httpx.AsyncClient() as client:
        if method == "get":
            response = await client.get(url, params=request.query_params)
        elif method == "post":
            response = await client.post(url, json=await request.json())
        elif method == "put":
            response = await client.put(url, json=await request.json())
        elif method == "delete":
            response = await client.delete(url)
        else:
            return {"error": "Unsupported method"}
    
    return response.json()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080) 