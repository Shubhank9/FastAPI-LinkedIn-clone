from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.company import Company
from app.schemas.company import CompanyResponse
from app.schemas.common import APIResponse


router = APIRouter(
    prefix="/companies",
    tags=["companies"]
)


@router.get(
    "/",
    response_model=APIResponse[list[CompanyResponse]],
    status_code=status.HTTP_200_OK
)
def get_all_companies(
    db: Session = Depends(get_db)
):
    statement = select(Company)

    companies = db.execute(statement).scalars().all()

    data = [
        CompanyResponse.model_validate(company)
        for company in companies
    ]

    return APIResponse[list[CompanyResponse]](
        success=True,
        message="Companies fetched successfully",
        status_code=status.HTTP_200_OK,
        data=data
    )