from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class ProfileCreate(BaseModel):
    user_id: str = Field(min_length=3, max_length=64)
    full_name: str = Field(min_length=1, max_length=128)
    email: EmailStr
    role: str = Field(default="student", max_length=64)


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=128)
    email: EmailStr | None = None
    role: str | None = Field(default=None, max_length=64)


class ProfileRead(BaseModel):
    id: int
    user_id: str
    full_name: str
    email: EmailStr
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}
