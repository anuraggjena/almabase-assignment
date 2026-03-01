from pydantic import BaseModel
from typing import List
from datetime import datetime
from .answer import AnswerItemResponse


class SessionResponse(BaseModel):
    id: int
    questionnaire_id: int
    created_at: datetime
    answers: List[AnswerItemResponse]