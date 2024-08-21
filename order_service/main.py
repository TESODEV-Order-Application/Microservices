from fastapi import FastAPI
from app.routes import router
import uvicorn
from fastapi_utils.tasks import repeat_every

app = FastAPI()

app.include_router(router)





@app.on_event("startup")
@repeat_every(wait_first=False,seconds=10)
async def startup_event():
    print("Email Loading Sequence has Started")
    #result = "await loadAllNews()"
    #print(result)






if __name__ == "__main__": 
    uvicorn.run(app, host="0.0.0.0", port=8002)