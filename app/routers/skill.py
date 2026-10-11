# GET /skills/
# GET /user-skills/
# POST /user-skills/
# DELETE /user-skills/{skill_id}


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependency import get_current_user_id
from app.models.skill import Skill
from app.models.user_skill import UserSkill
from app.schemas.skill import SkillResponse, UserSkillCreate
from app.schemas.common import APIResponse


skills_router = APIRouter(
    prefix="/skills",
    tags=["skills"]
)

user_skills_router = APIRouter(
    prefix="/user-skills",
    tags=["user skills"]
)



@skills_router.get(
    "/",
    response_model=APIResponse[list[SkillResponse]],
    status_code=status.HTTP_200_OK
)
def get_all_skills(
    db: Session = Depends(get_db)
):
    statement = select(Skill).order_by(Skill.name)
    skills = db.execute(statement).scalars().all()

    data = [
        SkillResponse.model_validate(skill)
        for skill in skills
    ]

    return APIResponse[list[SkillResponse]](
        success=True,
        message="Skills fetched successfully",
        status_code=status.HTTP_200_OK,
        data=data
    )



@user_skills_router.get(
    "/",
    response_model=APIResponse[list[SkillResponse]],
    status_code=status.HTTP_200_OK
)
def get_current_user_skills(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    statement = select(Skill).join(
        UserSkill,
        UserSkill.skill_id == Skill.id
    ).where(
        UserSkill.user_id == current_user_id
    )

    skills = db.execute(statement).scalars().all()

    data = [
        SkillResponse.model_validate(skill)
        for skill in skills
    ]

    return APIResponse[list[SkillResponse]](
        success=True,
        message="Skills fetched successfully",
        status_code=status.HTTP_200_OK,
        data=data
    )


@user_skills_router.post(
    "/",
    response_model=APIResponse[SkillResponse],
    status_code=status.HTTP_201_CREATED
)
def add_user_skill(
    skill_data: UserSkillCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    statement = select(Skill).where(
        Skill.id == skill_data.skill_id
    )
    skill = db.execute(statement).scalars().first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )

    statement = select(UserSkill).where(
        UserSkill.user_id == current_user_id,
        UserSkill.skill_id == skill_data.skill_id
    )
    existing = db.execute(statement).scalars().first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Skill is already associated with this user"
        )

    user_skill = UserSkill(
        user_id=current_user_id,
        skill_id=skill_data.skill_id
    )

    db.add(user_skill)
    db.commit()

    return APIResponse[SkillResponse](
        success=True,
        message="Skill added successfully",
        status_code=status.HTTP_201_CREATED,
        data=SkillResponse.model_validate(skill)
    )


@user_skills_router.delete(
    "/{skill_id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK
)
def remove_user_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    statement = select(UserSkill).where(
        UserSkill.user_id == current_user_id,
        UserSkill.skill_id == skill_id
    )

    user_skill = db.execute(statement).scalars().first()

    if not user_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill association not found"
        )

    db.delete(user_skill)
    db.commit()

    return APIResponse[None](
        success=True,
        message="Skill removed successfully",
        status_code=status.HTTP_200_OK,
        data=None
    )