# Importing Dependencies
import uvicorn
from fastapi import FastAPI

from API.upload import router as upload_router
from API.pipeline import router as pipeline_router

# FastAPI app
app = FastAPI()

# Including Routers
app.include_router(upload_router)
app.include_router(pipeline_router)

@app.get("/")
async def root():
    return {"message": "Dashboard API works!"}

if __name__ == "__main__":
    uvicorn.run("routes:app", host="0.0.0.0", port=8000)