# POST   /experiences
# GET    /experiences
# GET    /experiences/{experience_id}
# PATCH  /experiences/{experience_id}
# DELETE /experiences/{experience_id}


from fastapi import APIRouter , Depends , HTTPException , status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.experience import Experience
from app.schemas.experience import ExperienceCreate , ExperienceResponse , ExperienceUpdate
from app.schemas.common import APIResponse
from app.core.dependency import get_current_user_id , get_db


router = APIRouter(
    prefix="/experiences",
    tags=["experiences"]
)

@router.post(
    "/",
    response_model=APIResponse[ExperienceResponse],
    status_code=status.HTTP_201_CREATED
    )
def experience_create(
    exp_data : ExperienceCreate,
    db : Session = Depends(get_db),
    current_user_id : int = Depends(get_current_user_id)
):
    exp = Experience(
        user_id = current_user_id,
        **exp_data.model_dump()
    )

    db.add(exp)
    db.commit()
    db.refresh(exp)

    return APIResponse[ExperienceResponse](
        success=True,
        message="Experience added successful",
        status_code=status.HTTP_201_CREATED,
        data=ExperienceResponse.model_validate(exp),
    )


@router.get(
    "/",
    response_model=APIResponse[list[ExperienceResponse]],
    status_code=status.HTTP_200_OK
)
def get_experience(
    db : Session = Depends(get_db),
    current_user_id : int = Depends(get_current_user_id)
):
    statement = select(Experience).where(Experience.user_id == current_user_id)
    experiences = db.execute(statement).scalars().all()

    data = [ExperienceResponse.model_validate(exp) for exp in experiences]

    return APIResponse[list[ExperienceResponse]](
        success=True,
        message="Experiences fetched successful",
        status_code=status.HTTP_200_OK,
        data=data,
    ) 

@router.get(
    "/{exp_id}",
    response_model=APIResponse[ExperienceResponse],
    status_code=status.HTTP_200_OK
)
def get_experience_by_id(
    exp_id : int,
    db : Session = Depends(get_db),
    current_user_id : int = Depends(get_current_user_id)
):
    statement = select(Experience).where(
        Experience.id == exp_id,
        Experience.user_id == current_user_id
    )
    experience = db.execute(statement).scalars().first()

    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found."
        )

    return APIResponse[ExperienceResponse](
        success=True,
        message="Experience fetched successfully",
        status_code=status.HTTP_200_OK,
        data=ExperienceResponse.model_validate(experience)
    ) 

@router.patch(
        "/{exp_id}",
        response_model=APIResponse[ExperienceResponse],
        status_code=status.HTTP_200_OK
)
def updated_experience(
    exp_data : ExperienceUpdate,
    exp_id : int,
    db : Session = Depends(get_db),
    current_user_id : int = Depends(get_current_user_id)
):
    statement = select(Experience).where(
        Experience.id == exp_id , 
        Experience.user_id == current_user_id
        )

    experience = db.execute(statement).scalars().first()

    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )

    update_data = exp_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )
    for key, value in update_data.items():
        setattr(experience , key , value)

    db.commit()
    db.refresh(experience)

    return APIResponse[ExperienceResponse](
        success=True,
        message="Experience updated successfully",
        status_code=status.HTTP_200_OK,
        data=ExperienceResponse.model_validate(experience)
    )


@router.delete(
    "/{exp_id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK
)
def delete_experience(
    exp_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    statement = select(Experience).where(
        Experience.id == exp_id
    )
    result = db.execute(statement).scalars().first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )

    if result.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to perform this operation"
        )

    db.delete(result)
    db.commit()

    return APIResponse[None](
        success=True,
        message="Experience deleted successfully",
        status_code=status.HTTP_200_OK,
        data=None
    )