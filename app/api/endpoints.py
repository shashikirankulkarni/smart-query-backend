from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse, SyncRequest, SyncResponse
from app.services.query_service import process_query
from fastapi import Depends
from app.auth.dependencies import verify_token
from app.services.sync_service import sync_sheet

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
    
@router.post("/sync", response_model=SyncResponse, dependencies=[Depends(verify_token)])
def sync_sheet_data(data: SyncRequest):
    try:
        result = sync_sheet(data.sheet_url)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")