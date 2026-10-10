from typing import Optional
from fastapi import Cookie, Depends , HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.database import get_db
from app.core.security import verify_access_token
from app.models.user import User


def get_current_user(
        access_token : Optional[str] = Cookie(default=None),
        db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    try:                                              
        payload  = verify_access_token(access_token)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user_id = payload.get("sub")

    statement = select(User).where(User.id == int(user_id))
    result = db.execute(statement)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user