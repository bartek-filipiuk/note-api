from datetime import datetime

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)
    is_public: bool = False


class NoteUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    content: str | None = Field(None, min_length=1)
    tags: list[str] | None = None
    is_public: bool | None = None


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: list[str]
    is_public: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
