# POST   /profile
# GET    /profile/me
# PATCH  /profile/me
# DELETE /profile/me

from fastapi import APIRouter , Depends , status , HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.schemas.common import APIResponse
from app.models.profile import Profile
from app.models.user import User
from app.db.database import get_db
from app.core.dependency import get_current_user_id


router = APIRouter(
    prefix="/profile",
    tags=["profile"]
)


@router.post(
    "/",
    response_model=APIResponse[ProfileResponse],
    status_code=status.HTTP_201_CREATED
    )
def profile_create(
    profile_data : ProfileCreate,
    db : Session = Depends(get_db),
    current_user_id : int = Depends(get_current_user_id)
):
   statement = select(Profile).where(Profile.user_id == current_user_id)
   is_existing = db.execute(statement).scalars().first()

   if is_existing:
      raise HTTPException(
         status_code=status.HTTP_409_CONFLICT,
         detail="Profile already exist for this user"
      )

   profile = Profile(
      user_id = current_user_id,
      **profile_data.model_dump()
   )

   db.add(profile)
   db.commit()
   db.refresh(profile)

   return APIResponse[ProfileResponse](
           success=True,
           message="Profile created successfully",
           status_code=status.HTTP_201_CREATED,
           data=ProfileResponse.model_validate(profile),   # ORM object → schema
       )


@router.get(
   "/",
   response_model=APIResponse[ProfileResponse],
   status_code=status.HTTP_200_OK
)
def get_profiles(
   db : Session = Depends(get_db),
   current_user_id : int = Depends(get_current_user_id)
):
   statement = select(Profile).where(Profile.user_id == current_user_id)
   profile = db.execute(statement).scalars().first()

   if not profile:
      raise HTTPException(
         status_code=status.HTTP_404_NOT_FOUND,
         detail="Profile not found"
      )

   return APIResponse[ProfileResponse](
      success= True,
      message="Profile fetched successfully",
      status_code=status.HTTP_200_OK,
      data=ProfileResponse.model_validate(profile)
   )


@router.delete(
   "/",
   response_model=APIResponse[None],
   status_code=status.HTTP_200_OK
   )
def delete_profile(
   db : Session = Depends(get_db),
   current_user_id : int = Depends(get_current_user_id)
):
   statement = select(Profile).where(Profile.user_id == current_user_id)
   profile = db.execute(statement).scalars().first()

   if not profile:
      raise HTTPException(
         status_code = status.HTTP_404_NOT_FOUND,
         detail="Profile not exist"
      )

   db.delete(profile)
   db.commit()

   return APIResponse[None](
     success= True,
     message="Profile deleted successfully",
     status_code=status.HTTP_200_OK,
     data=None
   )


@router.patch(
   "/",
   response_model=APIResponse[ProfileResponse],
   status_code = status.HTTP_200_OK
)
def update_profile(
   profile_data : ProfileUpdate,
   db : Session = Depends(get_db),
   current_user_id : int = Depends(get_current_user_id)
):
   statement = select(Profile).where(Profile.user_id == current_user_id)
   profile = db.execute(statement).scalars().first()

   if not profile:
      raise HTTPException(
         status_code=status.HTTP_404_NOT_FOUND,
         detail = "The profile you are trying to update is not exist."
      )

   update_data = profile_data.model_dump(exclude_unset=True)

   if not update_data:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="No fields provided for update"
    )

   for key ,values in update_data.items():
      setattr(profile, key, values)

   db.commit()
   db.refresh(profile)

   return APIResponse[ProfileResponse](
        success= True,
        message="Profile updated successfully",
        status_code=status.HTTP_200_OK,
        data=ProfileResponse.model_validate(profile)
   )