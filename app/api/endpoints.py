from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.services.query_service import process_query
from fastapi import Depends
from app.auth.dependencies import verify_token

router = APIRouter()

@router.get("/health", dependencies=[Depends(verify_token)])
def health_check():
    return {"status": "ok"}

@router.post("/query", response_model=QueryResponse, dependencies=[Depends(verify_token)])
def query_sheet(data: QueryRequest):
    try:
        answer = process_query(data.sheet_url, data.question)
        return QueryResponse(answer=answer)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Server error: " + str(e))