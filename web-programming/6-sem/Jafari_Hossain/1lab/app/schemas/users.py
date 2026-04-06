from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from pydantic import ConfigDict

from app.schemas.domain import UserSkillRead


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    created_at: datetime


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserProfile(UserPublic):
    user_skills: list[UserSkillRead]

