import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.attachment import Attachment
from app.models.note import Note
from app.models.user import User

router = APIRouter(tags=["attachments"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


class AttachmentResponse(BaseModel):
    id: int
    note_id: int
    original_filename: str
    mime_type: str
    size_bytes: int

    model_config = {"from_attributes": True}


def _get_note_or_404(note_id: int, db: Session) -> Note:
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


def _check_note_owner(note: Note, user: User) -> None:
    if note.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.post(
    "/notes/{note_id}/attachments",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(
    note_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = _get_note_or_404(note_id, db)
    _check_note_owner(note, current_user)

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_MIME_TYPES)}",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: {MAX_FILE_SIZE} bytes",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "file")[1]
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, unique_filename)

    with open(filepath, "wb") as f:
        f.write(content)

    attachment = Attachment(
        note_id=note_id,
        filename=unique_filename,
        original_filename=file.filename or "unknown",
        mime_type=file.content_type,
        size_bytes=len(content),
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


@router.get("/notes/{note_id}/attachments", response_model=list[AttachmentResponse])
def list_attachments(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_note_or_404(note_id, db)
    attachments = db.query(Attachment).filter(Attachment.note_id == note_id).all()
    return attachments


@router.get("/notes/{note_id}/attachments/{attachment_id}")
def download_attachment(
    note_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_note_or_404(note_id, db)
    attachment = db.query(Attachment).filter(
        Attachment.id == attachment_id,
        Attachment.note_id == note_id,
    ).first()
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
    filepath = os.path.join(UPLOAD_DIR, attachment.filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on disk")
    return FileResponse(
        filepath,
        media_type=attachment.mime_type,
        filename=attachment.original_filename,
    )


@router.delete("/notes/{note_id}/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(
    note_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = _get_note_or_404(note_id, db)
    _check_note_owner(note, current_user)
    attachment = db.query(Attachment).filter(
        Attachment.id == attachment_id,
        Attachment.note_id == note_id,
    ).first()
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
    filepath = os.path.join(UPLOAD_DIR, attachment.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    db.delete(attachment)
    db.commit()
