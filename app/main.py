from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router

app = FastAPI(title="Smart Query API")

#Add CORS middleware configuration here
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or use ["*"] during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Customize OpenAPI schema with Bearer auth
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Smart Query API",
        version="1.0.0",
        description="API with Bearer Token Auth",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Set the custom OpenAPI schema
app.openapi = custom_openapi

# Include all API endpoints
app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "Smart Query API is running!"}