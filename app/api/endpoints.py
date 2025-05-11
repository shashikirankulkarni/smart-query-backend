from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse, SyncRequest, SyncResponse
from app.services.query_service import process_query
from fastapi import Depends
from app.auth.dependencies import verify_token
from app.services.sync_service import sync_sheet
from app.services.visit_service import get_total_visits

router = APIRouter()

@router.get("/visits")
def fetch_visits():
    try:
        visits = get_total_visits()
        return {"visits": visits}
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/query", response_model=QueryResponse, dependencies=[Depends(verify_token)])
def query_sheet(data: QueryRequest):
    try:
        print(f"📥 Received query for sheet: {data.sheet_url} | Question: {data.question}")
        answer = process_query(data.sheet_url, data.question)
        return QueryResponse(answer=answer)
    except ValueError as ve:
        print(f"❌ ValueError in query: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"🔥 Internal Server Error in query: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    
@router.post("/sync", response_model=SyncResponse, dependencies=[Depends(verify_token)])
def sync_sheet_data(data: SyncRequest):
    try:
        result = sync_sheet(data.sheet_url)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")