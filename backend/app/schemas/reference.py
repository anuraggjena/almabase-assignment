from pydantic import BaseModel


class ReferenceUploadResponse(BaseModel):
    document_id: int
    total_chunks: int