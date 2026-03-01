from sqlalchemy import Column, Integer, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class GeneratedAnswer(Base):
    __tablename__ = "generated_answers"

    id = Column(Integer, primary_key=True, index=True)

    generation_session_id = Column(
        Integer,
        ForeignKey("generation_sessions.id"),
        nullable=False
    )

    question_id = Column(
        Integer,
        ForeignKey("questions.id"),
        nullable=False
    )

    answer_text = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False)

    session = relationship("GenerationSession", back_populates="answers")
    question = relationship("Question")