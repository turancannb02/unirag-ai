from typing import List
from pydantic import BaseModel, Field


class Citation(BaseModel):
    source: str = Field(..., description="Source file name")
    page: int = Field(..., description="1-based page number")
    chunk_id: str = Field(..., description="Chunk identifier")


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    citations: List[Citation]
    disclaimer: str
