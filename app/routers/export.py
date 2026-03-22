import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.note import Note
from app.models.note_share import NoteShare
from app.models.user import User

router = APIRouter(tags=["export"])


@router.get("/notes/{note_id}/export")
def export_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    # Check access: owner, shared, or public
    has_access = (
        note.owner_id == current_user.id
        or note.is_public
        or db.query(NoteShare).filter(
            NoteShare.note_id == note_id,
            NoteShare.shared_with_user_id == current_user.id,
        ).first() is not None
    )
    if not has_access:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    tags = json.loads(note.tags) if note.tags else []
    tags_str = ", ".join(tags) if tags else "(brak)"
    content = f"Tytuł: {note.title}\nTagi: {tags_str}\n\n{note.content}\n"

    return PlainTextResponse(
        content=content,
        headers={"Content-Disposition": f'attachment; filename="{note.title}.txt"'},
    )
