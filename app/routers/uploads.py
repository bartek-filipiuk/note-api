import os
import tempfile
import uuid

import anyio

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.limiter import limiter
from app.models.attachment import Attachment
from app.models.user import User
from app.services.notes import check_note_access, check_note_owner, get_note_or_404

router = APIRouter(tags=["attachments"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
CHUNK_SIZE = 1024 * 1024  # 1 MB

MAGIC_BYTES = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/gif": [b"GIF87a", b"GIF89a"],
}


def _validate_magic_bytes(content: bytes, claimed_mime: str) -> bool:
    if claimed_mime == "image/webp":
        return len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP"
    signatures = MAGIC_BYTES.get(claimed_mime)
    if signatures is None:
        return False
    return any(content.startswith(sig) for sig in signatures)


class AttachmentResponse(BaseModel):
    id: int
    note_id: int
    original_filename: str
    mime_type: str
    size_bytes: int

    model_config = {"from_attributes": True}


@router.post(
    "/notes/{note_id}/attachments",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/minute")
async def upload_attachment(
    request: Request,
    note_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = get_note_or_404(note_id, db)
    check_note_owner(note, current_user)

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_MIME_TYPES)}",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "file")[1]
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, unique_filename)

    # Stream to temp file with early size limit enforcement
    header = bytearray()
    total_size = 0
    tmp_fd, tmp_path = tempfile.mkstemp(dir=UPLOAD_DIR)
    try:
        with os.fdopen(tmp_fd, "wb") as tmp:
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File too large. Max size: {MAX_FILE_SIZE} bytes",
                    )
                if len(header) < 12:
                    header.extend(chunk[: 12 - len(header)])
                await anyio.to_thread.run_sync(tmp.write, chunk)

        # Validate magic bytes against claimed MIME type
        if not _validate_magic_bytes(bytes(header), file.content_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File content does not match declared type",
            )

        os.rename(tmp_path, filepath)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise

    attachment = Attachment(
        note_id=note_id,
        filename=unique_filename,
        original_filename=file.filename or "unknown",
        mime_type=file.content_type,
        size_bytes=total_size,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


@router.get("/notes/{note_id}/attachments", response_model=list[AttachmentResponse])
@limiter.limit("30/minute")
def list_attachments(
    request: Request,
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = get_note_or_404(note_id, db)
    check_note_access(note, current_user, db)
    attachments = db.query(Attachment).filter(Attachment.note_id == note_id).all()
    return attachments


@router.get("/notes/{note_id}/attachments/{attachment_id}")
@limiter.limit("30/minute")
def download_attachment(
    request: Request,
    note_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = get_note_or_404(note_id, db)
    check_note_access(note, current_user, db)
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
@limiter.limit("10/minute")
def delete_attachment(
    request: Request,
    note_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = get_note_or_404(note_id, db)
    check_note_owner(note, current_user)
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
