from pydantic import BaseModel, HttpUrl

class QueryRequest(BaseModel):
    sheet_url: HttpUrl
    question: str

class QueryResponse(BaseModel):
    answer: str