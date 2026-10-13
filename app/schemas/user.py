# this is for the aggregate profile schema which will be used to return the profile data along with the user data and skills data

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.education import EducationResponse
from app.schemas.experience import ExperienceResponse
from app.schemas.post import PostResponse
from app.schemas.profile import ProfileResponse
from app.schemas.skill import SkillResponse


class UserBasic(BaseModel):
    id: int
    name: str
    # only returned on /users/me, hidden when viewing someone else's profile
    email: Optional[EmailStr] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class UserExperience(ExperienceResponse):
    company_name: str


class UserEducation(EducationResponse):
    institution_name: str


class UserFullProfile(BaseModel):
    user: UserBasic
    profile: Optional[ProfileResponse]
    experiences: list[UserExperience]
    educations: list[UserEducation]
    skills: list[SkillResponse]
    posts: list[PostResponse]
