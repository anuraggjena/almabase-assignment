from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi.responses import StreamingResponse

from app.database import get_db
from app.models import (
    Question,
    Questionnaire,
    DocumentChunk,
    ReferenceDocument,
    GenerationSession,
    GeneratedAnswer
)
from app.core.security import get_current_user
from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.answer_generation_service import generate_answer
from app.services.export_service import export_docx, export_pdf, export_txt

router = APIRouter(prefix="/answers", tags=["Answer Generation"])



# generate answers

@router.post("/generate/{questionnaire_id}")
def generate_answers(
    questionnaire_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == questionnaire_id,
        Questionnaire.user_id == current_user.id
    ).first()

    if not questionnaire:
        raise HTTPException(status_code=403, detail="Unauthorized access.")

    questions = db.query(Question).filter(
        Question.questionnaire_id == questionnaire_id
    ).order_by(Question.order_index.asc()).all()

    if not questions:
        raise HTTPException(status_code=404, detail="No questions found.")

    user_documents = db.query(ReferenceDocument).filter(
        ReferenceDocument.user_id == current_user.id
    ).all()

    if not user_documents:
        raise HTTPException(status_code=400, detail="No reference documents uploaded.")

    document_ids = [doc.id for doc in user_documents]

    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.document_id.in_(document_ids)
    ).all()

    if not chunks:
        raise HTTPException(status_code=400, detail="No reference content available.")

    # Create new generation session
    session_label = f"{questionnaire.original_filename} - {datetime.utcnow().strftime('%d %b %Y %H:%M')}"

    new_session = GenerationSession(
        questionnaire_id=questionnaire.id,
        user_id=current_user.id,
        session_name=session_label
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    results = []

    for q in questions:

        relevant_chunks, confidence = retrieve_relevant_chunks(
            q.question_text,
            chunks
        )

        # block generation if no relevant chunks
        if not relevant_chunks:
            answer_text = "Not found in references."
            citations = []
            confidence = 0.0
        else:
            generated = generate_answer(
                q.question_text,
                relevant_chunks
            )
            answer_text = generated["answer"].strip()

            if answer_text == "Not found in references.":
                citations = []
                confidence = 0.0
            else:
                citations = generated["citations"]

        new_answer = GeneratedAnswer(
            generation_session_id=new_session.id,
            question_id=q.id,
            answer_text=answer_text,
            confidence_score=confidence
        )

        db.add(new_answer)

        results.append({
            "question_id": q.id,
            "question": q.question_text,
            "answer": answer_text,
            "confidence_score": confidence,
            "citations": citations
        })

    db.commit()

    return {
        "generation_session_id": new_session.id,
        "total_questions": len(results),
        "results": results
    }

# User-Based History

@router.get("/sessions")
def list_all_sessions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    sessions = db.query(GenerationSession).filter(
        GenerationSession.user_id == current_user.id
    ).order_by(desc(GenerationSession.created_at)).all()

    return {
        "total_sessions": len(sessions),
        "sessions": [
            {
                "session_id": s.id,
                "session_name": s.session_name,
                "created_at": s.created_at
            }
            for s in sessions
        ]
    }

# Session-Based History

@router.get("/session/{session_id}")
def get_session_answers(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    session = db.query(GenerationSession).filter(
        GenerationSession.id == session_id,
        GenerationSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    answers = db.query(GeneratedAnswer).filter(
        GeneratedAnswer.generation_session_id == session_id
    ).all()

    results = []

    for ans in answers:
        results.append({
            "question_id": ans.question_id,
            "question": ans.question.question_text,
            "answer": ans.answer_text,
            "confidence_score": ans.confidence_score,
            "citations": []  # Not persisted
        })

    return {
        "session_id": session.id,
        "questionnaire_id": session.questionnaire_id,
        "created_at": session.created_at,
        "total_answers": len(results),
        "results": results
    }

# manual edit answer

@router.put("/session/{session_id}/answer/{question_id}")
def update_answer(
    session_id: int,
    question_id: int,
    updated_text: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    session = db.query(GenerationSession).filter(
        GenerationSession.id == session_id,
        GenerationSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=403, detail="Unauthorized access.")

    answer = db.query(GeneratedAnswer).filter(
        GeneratedAnswer.generation_session_id == session_id,
        GeneratedAnswer.question_id == question_id
    ).first()

    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found.")

    answer.answer_text = updated_text["answer"]
    db.commit()

    return {
        "message": "Answer updated successfully.",
        "answer": answer.answer_text
    }

# regenerate single answer

@router.post("/session/{session_id}/regenerate/{question_id}")
def regenerate_single_answer(
    session_id: int,
    question_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    session = db.query(GenerationSession).filter(
        GenerationSession.id == session_id,
        GenerationSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=403, detail="Unauthorized.")

    answer = db.query(GeneratedAnswer).filter(
        GeneratedAnswer.generation_session_id == session_id,
        GeneratedAnswer.question_id == question_id
    ).first()

    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found.")

    question = answer.question

    user_documents = db.query(ReferenceDocument).filter(
        ReferenceDocument.user_id == current_user.id
    ).all()

    document_ids = [doc.id for doc in user_documents]

    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.document_id.in_(document_ids)
    ).all()

    relevant_chunks, confidence = retrieve_relevant_chunks(
        question.question_text,
        chunks
    )

    if not relevant_chunks:
        answer_text = "Not found in references."
        citations = []
        confidence = 0.0
    else:
        generated = generate_answer(
            question.question_text,
            relevant_chunks
        )
        answer_text = generated["answer"].strip()

        if answer_text == "Not found in references.":
            citations = []
            confidence = 0.0
        else:
            citations = generated["citations"]

    answer.answer_text = answer_text
    answer.confidence_score = confidence

    db.commit()

    return {
        "answer": answer_text,
        "confidence_score": confidence,
        "citations": citations
    }

# export session

@router.get("/export/{session_id}/{format}")
def export_session(
    session_id: int,
    format: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    session = db.query(GenerationSession).filter(
        GenerationSession.id == session_id,
        GenerationSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    questionnaire = session.questionnaire

    questions = db.query(Question).filter(
        Question.questionnaire_id == questionnaire.id
    ).order_by(Question.order_index.asc()).all()

    answers = db.query(GeneratedAnswer).filter(
        GeneratedAnswer.generation_session_id == session_id
    ).all()

    question_data = [
        {"id": q.id, "order": q.order_index, "text": q.question_text}
        for q in questions
    ]

    answer_data = [
        {
            "question_id": a.question_id,
            "answer": a.answer_text,
            "confidence_score": a.confidence_score,
            "citations": []
        }
        for a in answers
    ]

    format = format.lower()

    if format == "docx":
        file_stream = export_docx(question_data, answer_data)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        extension = "docx"

    elif format == "pdf":
        file_stream = export_pdf(question_data, answer_data)
        media_type = "application/pdf"
        extension = "pdf"

    elif format == "txt":
        file_stream = export_txt(question_data, answer_data)
        media_type = "text/plain"
        extension = "txt"

    else:
        raise HTTPException(status_code=400, detail="Invalid export format.")

    filename = f"questionnaire_session_{session_id}.{extension}"

    return StreamingResponse(
        file_stream,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

# delete session

@router.delete("/session/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    session = db.query(GenerationSession).filter(
        GenerationSession.id == session_id,
        GenerationSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Delete related answers first (safe even if cascade exists)
    db.query(GeneratedAnswer).filter(
        GeneratedAnswer.generation_session_id == session_id
    ).delete()

    db.delete(session)
    db.commit()

    return {"message": "Session deleted successfully."}