# POST   /auth/register
# POST   /auth/login
# GET    /auth/me
# POST   /auth/logout

from fastapi import APIRouter, Depends, HTTPException, status , Response
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.database import get_db
from app.schemas.auth import UserCreate , UserResponse , LoginRequest
from app.schemas.common import APIResponse
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token  
from app.core.dependency import get_current_user

router = APIRouter(
    prefix="/auth", 
    tags=["auth"]
)

@router.post(
    "/register",
    response_model=APIResponse[UserResponse])
def register_user (
    user_data : UserCreate,
    db : Session = Depends(get_db)
):
    statement = select(User).where(User.email == user_data.email)
    existing_user = db.execute(statement).scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    hashed_password = hash_password(user_data.password)
    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return APIResponse[UserResponse](
        success=True,
        message="User registered successfully",
        status_code=status.HTTP_201_CREATED,
        data=UserResponse.model_validate(user),   # ORM object → schema
    )


@router.post(
        "/login",
        response_model=APIResponse[UserResponse])
def user_login(
  response : Response,  
  user_data :  LoginRequest ,
  db : Session = Depends(get_db)
):
    statement = select(User).where(User.email == user_data.email)
    result = db.execute(statement)
    user = result.scalars().first()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(user.id)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=30 * 60
    )

    return APIResponse[UserResponse](
        success=True,
        message="Login successful",
        status_code=status.HTTP_200_OK,
        data=UserResponse.model_validate(user),
    )

@router.get("/me" , response_model=APIResponse[UserResponse])
def get_user_details(
    current_user : User = Depends(get_current_user)
):
    return APIResponse[UserResponse](
            success=True,
            message="User details found successfully!",
            status_code=status.HTTP_200_OK,
            data=UserResponse.model_validate(current_user),
        )

@router.post(
        "/logout",
        response_model=APIResponse[None])
def user_logout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        secure=True,
        samesite="lax"
    )

    return APIResponse[None](
        success=True,
        message="Logout successful",
        status_code=status.HTTP_200_OK,
        data=None,
    )