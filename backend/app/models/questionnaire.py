from sqlalchemy import Column, Integer, String, Text, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from app.database import Base

class Questionnaire(Base):
    __tablename__ = "questionnaires"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    original_filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    original_content = Column(LargeBinary, nullable=False)

    user = relationship("User")
    questions = relationship("Question")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    questionnaire_id = Column(Integer, ForeignKey("questionnaires.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    order_index = Column(Integer, nullable=False)

    questionnaire = relationship("Questionnaire", back_populates="questions")