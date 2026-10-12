# POST   /educations
# GET    /educations
# GET    /educations/{education_id}
# PATCH  /educations/{education_id}
# DELETE /educations/{education_id}


from fastapi import APIRouter , Depends , HTTPException , status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.education import Education
from app.models.institution import Institution
from app.schemas.education import EducationCreate , EducationResponse , EducationUpdate
from app.schemas.common import APIResponse
from app.core.dependency import get_current_user_id , get_db


router = APIRouter(
    prefix="/educations",
    tags=["educations"]
)


@router.post(
    "/",
    response_model=APIResponse[EducationResponse],
    status_code=status.HTTP_201_CREATED
    )
def education_create(
    edu_data : EducationCreate,
    db : Session = Depends(get_db),
    current_user_id : int = Depends(get_current_user_id)
):
    statement = select(Institution).where(
        Institution.id == edu_data.institution_id
    )
    institution = db.execute(statement).scalars().first()

    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institution not found"
        )

    edu = Education(
        user_id = current_user_id,
        **edu_data.model_dump()
    )

    db.add(edu)
    db.commit()
    db.refresh(edu)

    return APIResponse[EducationResponse](
        success=True,
        message="Education added successful",
        status_code=status.HTTP_201_CREATED,
        data=EducationResponse.model_validate(edu),
    )


@router.get(
    "/",
    response_model=APIResponse[list[EducationResponse]],
    status_code=status.HTTP_200_OK
)
def get_educations(
    db : Session = Depends(get_db),
    current_user_id : int = Depends(get_current_user_id)
):
    statement = select(Education).where(Education.user_id == current_user_id)
    education = db.execute(statement).scalars().all()

    data = [EducationResponse.model_validate(edu) for edu in education]

    return APIResponse[list[EducationResponse]](
        success=True,
        message="Educations fetched successful",
        status_code=status.HTTP_200_OK,
        data=data,
    ) 

@router.get(
    "/{edu_id}",
    response_model=APIResponse[EducationResponse],
    status_code=status.HTTP_200_OK
)
def get_education_by_id(
    edu_id : int,
    db : Session = Depends(get_db),
    current_user_id : int = Depends(get_current_user_id)
):
    statement = select(Education).where(
        Education.id == edu_id,
        Education.user_id == current_user_id
    )
    education = db.execute(statement).scalars().first()

    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education not found."
        )

    return APIResponse[EducationResponse](
        success=True,
        message="Educations fetched successfully",
        status_code=status.HTTP_200_OK,
        data=EducationResponse.model_validate(education)
    ) 

@router.patch(
        "/{edu_id}",
        response_model=APIResponse[EducationResponse],
        status_code=status.HTTP_200_OK
)
def updated_education(
    edu_data : EducationUpdate,
    edu_id : int,
    db : Session = Depends(get_db),
    current_user_id : int = Depends(get_current_user_id)
):
    statement = select(Education).where(
        Education.id == edu_id , 
        Education.user_id == current_user_id
        )

    education = db.execute(statement).scalars().first()

    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education not found"
        )

    update_data = edu_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    if "institution_id" in update_data:
        statement = select(Institution).where(
            Institution.id == update_data["institution_id"]
        )
        institution = db.execute(statement).scalars().first()

        if not institution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institution not found"
            )

    for key, value in update_data.items():
        setattr(education , key , value)

    db.commit()
    db.refresh(education)

    return APIResponse[EducationResponse](
        success=True,
        message="Education updated successfully",
        status_code=status.HTTP_200_OK,
        data=EducationResponse.model_validate(education)
    )


@router.delete(
    "/{edu_id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK
)
def delete_education(
    edu_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    statement = select(Education).where(
        Education.id == edu_id,
        Education.user_id == current_user_id
    )
    result = db.execute(statement).scalars().first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education not found"
        )

    db.delete(result)
    db.commit()

    return APIResponse[None](
        success=True,
        message="Education deleted successfully",
        status_code=status.HTTP_200_OK,
        data=None
    )
