from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.note import Note
from app.models.note_share import NoteShare
from app.models.user import User


def get_note_or_404(note_id: int, db: Session) -> Note:
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


def has_share_access(note_id: int, user_id: int, db: Session) -> bool:
    return db.query(NoteShare).filter(
        NoteShare.note_id == note_id,
        NoteShare.shared_with_user_id == user_id,
    ).first() is not None


def check_note_access(note: Note, user: User, db: Session) -> None:
    if note.owner_id == user.id:
        return
    if note.is_public:
        return
    if has_share_access(note.id, user.id, db):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


def check_note_owner(note: Note, user: User) -> None:
    if note.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
