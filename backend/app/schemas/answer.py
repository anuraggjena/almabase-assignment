from pydantic import BaseModel
from typing import List


class CitationResponse(BaseModel):
    document_id: int
    chunk_index: int
    snippet: str


class AnswerItemResponse(BaseModel):
    question_id: int
    question: str
    answer: str
    citations: List[CitationResponse]
    confidence: float


class GenerateAnswersResponse(BaseModel):
    total_questions: int
    results: List[AnswerItemResponse]