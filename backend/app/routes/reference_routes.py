from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ReferenceDocument, DocumentChunk
from app.core.security import get_current_user
from app.services.files_extraction_service import extract_text_from_file
from app.services.chunking_service import chunk_text

router = APIRouter(prefix="/references", tags=["Reference Documents"])


@router.post("/upload")
def upload_reference_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    try:
        text = extract_text_from_file(file.file, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if len(text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Reference document too short.")

    # delete old references & chunks for this user
    user_documents = db.query(ReferenceDocument).filter(
        ReferenceDocument.user_id == current_user.id
    ).all()

    for doc in user_documents:
        db.query(DocumentChunk).filter(
            DocumentChunk.document_id == doc.id
        ).delete()

    db.query(ReferenceDocument).filter(
        ReferenceDocument.user_id == current_user.id
    ).delete()

    db.commit()

    # insert new document
    document = ReferenceDocument(
        user_id=current_user.id,
        filename=file.filename,
        full_text=text,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # create chunks
    chunk_data = chunk_text(text)

    for chunk in chunk_data:
        db_chunk = DocumentChunk(
            document_id=document.id,
            chunk_index=chunk["chunk_index"],
            chunk_text=chunk["chunk_text"]
        )
        db.add(db_chunk)

    db.commit()

    return {
        "message": "Reference document replaced successfully.",
        "document_id": document.id,
        "total_chunks": len(chunk_data),
    }