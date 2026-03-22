import json
import os

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.limiter import limiter
from app.models.note import Note
from app.models.note_share import NoteShare
from app.models.user import User
from app.schemas.notes import NoteCreate, NoteResponse, NoteUpdate
from app.models.attachment import Attachment
from app.routers.uploads import UPLOAD_DIR
from app.services.notes import check_note_access, check_note_owner, get_note_or_404

router = APIRouter(prefix="/notes", tags=["notes"])


class ShareRequest(BaseModel):
    user_id: int


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


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
def create_note(
    request: Request,
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
@limiter.limit("60/minute")
def list_notes(
    request: Request,
    tag: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    shared_note_ids = [
        s.note_id
        for s in db.query(NoteShare.note_id).filter(
            NoteShare.shared_with_user_id == current_user.id
        ).all()
    ]

    query = db.query(Note).filter(
        or_(
            Note.owner_id == current_user.id,
            Note.id.in_(shared_note_ids) if shared_note_ids else False,
            Note.is_public == True,
        )
    )

    notes = query.all()

    if tag:
        notes = [n for n in notes if tag in (json.loads(n.tags) if n.tags else [])]

    return [_note_to_response(n) for n in notes]


@router.get("/{note_id}", response_model=NoteResponse)
@limiter.limit("60/minute")
def get_note(
    request: Request,
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = get_note_or_404(note_id, db)
    check_note_access(note, current_user, db)
    return _note_to_response(note)


@router.put("/{note_id}", response_model=NoteResponse)
@limiter.limit("30/minute")
def update_note(
    request: Request,
    note_id: int,
    data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = get_note_or_404(note_id, db)
    check_note_owner(note, current_user)
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
@limiter.limit("30/minute")
def delete_note(
    request: Request,
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = get_note_or_404(note_id, db)
    check_note_owner(note, current_user)
    # Clean up attachment files from disk before deleting note
    attachments = db.query(Attachment).filter(Attachment.note_id == note_id).all()
    for att in attachments:
        filepath = os.path.join(UPLOAD_DIR, att.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    db.delete(note)
    db.commit()


@router.post("/{note_id}/share", status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
def share_note(
    request: Request,
    note_id: int,
    data: ShareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = get_note_or_404(note_id, db)
    check_note_owner(note, current_user)
    target_user = db.query(User).filter(User.id == data.user_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    existing = db.query(NoteShare).filter(
        NoteShare.note_id == note_id,
        NoteShare.shared_with_user_id == data.user_id,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already shared",
        )
    share = NoteShare(note_id=note_id, shared_with_user_id=data.user_id)
    db.add(share)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already shared",
        ) from None
    return {"detail": "Note shared successfully"}


@router.delete("/{note_id}/share/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
def unshare_note(
    request: Request,
    note_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = get_note_or_404(note_id, db)
    check_note_owner(note, current_user)
    share = db.query(NoteShare).filter(
        NoteShare.note_id == note_id,
        NoteShare.shared_with_user_id == user_id,
    ).first()
    if not share:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share not found")
    db.delete(share)
    db.commit()
