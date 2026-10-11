# GET /institutions


from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.institution import Institution
from app.schemas.institution import InstitutionResponse
from app.schemas.common import APIResponse


router = APIRouter(
    prefix="/institutions",
    tags=["institutions"]
)


@router.get(
    "/",
    response_model=APIResponse[list[InstitutionResponse]],
    status_code=status.HTTP_200_OK
)
def get_all_institutions(
    db: Session = Depends(get_db)
):
    statement = select(Institution).order_by(Institution.name)
    institutions = db.execute(statement).scalars().all()

    data = [
        InstitutionResponse.model_validate(institution)
        for institution in institutions
    ]

    return APIResponse[list[InstitutionResponse]](
        success=True,
        message="Institutions fetched successfully",
        status_code=status.HTTP_200_OK,
        data=data
    )
