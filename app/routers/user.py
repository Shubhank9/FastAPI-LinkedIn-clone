# GET    /users/me
# GET    /users/{user_id}

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependency import get_current_user_id
from app.db.database import get_db
from app.models.company import Company
from app.models.education import Education
from app.models.experience import Experience
from app.models.institution import Institution
from app.models.post import Post
from app.models.profile import Profile
from app.models.skill import Skill
from app.models.user import User
from app.models.user_skill import UserSkill
from app.schemas.common import APIResponse
from app.schemas.education import EducationResponse
from app.schemas.experience import ExperienceResponse
from app.schemas.post import PostResponse
from app.schemas.profile import ProfileResponse
from app.schemas.skill import SkillResponse
from app.schemas.user import UserBasic, UserEducation, UserExperience, UserFullProfile


router = APIRouter(
    prefix="/users",
    tags=["users"]
)


def build_full_profile(db: Session, user_id: int, include_email: bool) -> UserFullProfile:
    user = db.execute(
        select(User).where(User.id == user_id)
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    profile = db.execute(
        select(Profile).where(Profile.user_id == user_id)
    ).scalars().first()

    experience_rows = db.execute(
        select(Experience, Company.name)
        .join(Company, Company.id == Experience.company_id)
        .where(Experience.user_id == user_id)
        .order_by(Experience.start_date.desc())
    ).all()

    education_rows = db.execute(
        select(Education, Institution.name)
        .join(Institution, Institution.id == Education.institution_id)
        .where(Education.user_id == user_id)
        .order_by(Education.start_date.desc().nulls_last())
    ).all()

    skills = db.execute(
        select(Skill)
        .join(UserSkill, UserSkill.skill_id == Skill.id)
        .where(UserSkill.user_id == user_id)
        .order_by(Skill.name)
    ).scalars().all()

    posts = db.execute(
        select(Post)
        .where(Post.user_id == user_id)
        .order_by(Post.created_at.desc())
    ).scalars().all()

    user_data = UserBasic.model_validate(user)
    if not include_email:
        user_data.email = None

    return UserFullProfile(
        user=user_data,
        profile=ProfileResponse.model_validate(profile) if profile else None,
        experiences=[
            UserExperience(
                **ExperienceResponse.model_validate(exp).model_dump(),
                company_name=company_name
            )
            for exp, company_name in experience_rows
        ],
        educations=[
            UserEducation(
                **EducationResponse.model_validate(edu).model_dump(),
                institution_name=institution_name
            )
            for edu, institution_name in education_rows
        ],
        skills=[SkillResponse.model_validate(skill) for skill in skills],
        posts=[PostResponse.model_validate(post) for post in posts],
    )


@router.get(
    "/me",
    response_model=APIResponse[UserFullProfile],
    status_code=status.HTTP_200_OK
)
def get_my_full_profile(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    data = build_full_profile(db, current_user_id, include_email=True)

    return APIResponse[UserFullProfile](
        success=True,
        message="User profile fetched successfully",
        status_code=status.HTTP_200_OK,
        data=data
    )


@router.get(
    "/{user_id}",
    response_model=APIResponse[UserFullProfile],
    status_code=status.HTTP_200_OK
)
def get_user_full_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    # viewing your own id behaves the same as /users/me
    data = build_full_profile(db, user_id, include_email=(user_id == current_user_id))

    return APIResponse[UserFullProfile](
        success=True,
        message="User profile fetched successfully",
        status_code=status.HTTP_200_OK,
        data=data
    )
