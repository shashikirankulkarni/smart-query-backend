from pydantic import BaseModel, HttpUrl

class QueryRequest(BaseModel):
    sheet_url: HttpUrl
    question: str

class QueryResponse(BaseModel):
    answer: str
    
class SyncRequest(BaseModel):
    sheet_url: HttpUrl

class SyncResponse(BaseModel):
    columns: list[str]
    row_count: int