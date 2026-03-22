import json
from urllib.parse import quote

from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.limiter import limiter
from app.models.user import User
from app.services.notes import check_note_access, get_note_or_404

router = APIRouter(tags=["export"])


@router.get("/notes/{note_id}/export")
@limiter.limit("20/minute")
def export_note(
    request: Request,
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = get_note_or_404(note_id, db)
    check_note_access(note, current_user, db)

    try:
        tags = json.loads(note.tags) if note.tags else []
        if not isinstance(tags, list):
            tags = []
    except json.JSONDecodeError:
        tags = []

    tags_str = ", ".join(tags) if tags else "(brak)"
    content = f"Tytuł: {note.title}\nTagi: {tags_str}\n\n{note.content}\n"

    safe_title = (note.title or "note").replace("\r", "").replace("\n", "").strip() or "note"
    filename = quote(f"{safe_title}.txt")

    return PlainTextResponse(
        content=content,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )
