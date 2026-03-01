from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Questionnaire, Question
from app.core.security import get_current_user
from app.services.files_extraction_service import extract_text_from_file
from app.services.question_parser import parse_numbered_questions

router = APIRouter(prefix="/questionnaires", tags=["Questionnaires"])


@router.post("/upload")
async def upload_questionnaire(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # File validation
    allowed_extensions = (".pdf", ".txt", ".docx")

    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Allowed formats: PDF, TXT, DOCX."
        )

    try:
        text = extract_text_from_file(file.file, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    questions = parse_numbered_questions(text)

    if not questions:
        raise HTTPException(
            status_code=400,
            detail="No numbered questions detected. Please upload a properly formatted questionnaire."
        )

    file_bytes = await file.read()

    questionnaire = Questionnaire(
        user_id=current_user.id,
        original_filename=file.filename,
        file_type=file.filename.split(".")[-1].lower(),
        original_content=file_bytes
    )

    db.add(questionnaire)
    db.commit()
    db.refresh(questionnaire)

    structured_response = []

    for q in questions:
        question = Question(
            questionnaire_id=questionnaire.id,
            question_text=q["text"],
            order_index=q["order"]
        )
        db.add(question)

        structured_response.append(q)

    db.commit()

    return {
        "message": "Questionnaire uploaded successfully.",
        "questionnaire_id": questionnaire.id,
        "total_questions": len(structured_response),
        "questions": structured_response
    }

@router.get("/my")
def get_my_questionnaires(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    questionnaires = db.query(Questionnaire).filter(
        Questionnaire.user_id == current_user.id
    ).order_by(Questionnaire.id.desc()).all()

    return {
        "questionnaires": [
            {
                "id": q.id,
                "total_questions": len(q.questions)
            }
            for q in questionnaires
        ]
    }