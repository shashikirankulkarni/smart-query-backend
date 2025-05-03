from fastapi import FastAPI
from app.api.endpoints import router as api_router
from fastapi.openapi.utils import get_openapi

app = FastAPI(title="Smart Query API")

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