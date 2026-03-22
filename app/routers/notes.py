import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.note import Note
from app.models.user import User
from app.schemas.notes import NoteCreate, NoteResponse, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


def _note_to_response(note: Note) -> dict:
    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "tags": json.loads(note.tags) if note.tags else [],
        "is_public": note.is_public,
        "owner_id": note.owner_id,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
    }


def _get_note_or_404(note_id: int, db: Session) -> Note:
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


def _check_note_access(note: Note, user: User) -> None:
    if note.owner_id == user.id:
        return
    if note.is_public:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


def _check_note_owner(note: Note, user: User) -> None:
    if note.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = Note(
        title=data.title,
        content=data.content,
        tags=json.dumps(data.tags),
        is_public=data.is_public,
        owner_id=current_user.id,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return _note_to_response(note)


@router.get("", response_model=list[NoteResponse])
def list_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notes = db.query(Note).filter(Note.owner_id == current_user.id).all()
    return [_note_to_response(n) for n in notes]


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = _get_note_or_404(note_id, db)
    _check_note_access(note, current_user)
    return _note_to_response(note)


@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = _get_note_or_404(note_id, db)
    _check_note_owner(note, current_user)
    if data.title is not None:
        note.title = data.title
    if data.content is not None:
        note.content = data.content
    if data.tags is not None:
        note.tags = json.dumps(data.tags)
    if data.is_public is not None:
        note.is_public = data.is_public
    db.commit()
    db.refresh(note)
    return _note_to_response(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = _get_note_or_404(note_id, db)
    _check_note_owner(note, current_user)
    db.delete(note)
    db.commit()
