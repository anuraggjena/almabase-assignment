from pydantic import BaseModel
from typing import List


class QuestionnaireUploadResponse(BaseModel):
    questionnaire_id: int
    total_questions: int


class QuestionResponse(BaseModel):
    id: int
    order_index: int
    question_text: str


class QuestionnaireDetailResponse(BaseModel):
    questionnaire_id: int
    original_filename: str
    total_questions: int
    questions: List[QuestionResponse]