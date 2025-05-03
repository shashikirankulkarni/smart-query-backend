from fastapi import FastAPI
from app.api.endpoints import router as api_router

app = FastAPI(title="Smart Query API")

# Include all endpoints
app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "Smart Query API is running!"}