# POST   /posts
# GET    /posts
# GET    /posts/me     > this should me above the /:id other wise me will be consider as post_id.
# GET    /posts/{post_id}
# PATCH  /posts/{post_id}
# DELETE /posts/{post_id}


from fastapi import APIRouter , status , Depends , HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.schemas.post import PostResponse ,PostCreate , PostUpdate
from app.schemas.common import APIResponse
from app.core.dependency import get_current_user_id , get_db
from app.models.post import Post



router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

@router.post(
    "/",
    response_model = APIResponse[PostResponse],
    status_code = status.HTTP_201_CREATED
)
def create_post(
    post_data : PostCreate,
    db : Session = Depends(get_db),
    current_user_id : int = Depends(get_current_user_id)
):
    post = Post(
        user_id = current_user_id,
        **post_data.model_dump()
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return APIResponse[PostResponse](
        success=True,
        message="Post created successfully",
        status_code=status.HTTP_201_CREATED,
        data=PostResponse.model_validate(post),
    )

@router.get(
    "/",
    response_model = APIResponse[list[PostResponse]],
    status_code = status.HTTP_200_OK
)
def get_all_posts(
   db : Session = Depends(get_db),
   current_user_id : int = Depends(get_current_user_id)
):
    statement = select(Post).where(Post.user_id != current_user_id)
    posts = db.execute(statement).scalars().all()

    data = [PostResponse.model_validate(post) for post in posts]

    return APIResponse[list[PostResponse]](
        success=True,
        message="Posts fetched successfully",
        status_code=status.HTTP_200_OK,
        data=data,
    )

@router.get(
    "/me",
    response_model = APIResponse[list[PostResponse]],
    status_code = status.HTTP_200_OK
)
def get_my_posts(
   db : Session = Depends(get_db),
   current_user_id : int = Depends(get_current_user_id)
):
    statement = select(Post).where(Post.user_id == current_user_id)
    posts = db.execute(statement).scalars().all()

    data = [PostResponse.model_validate(post) for post in posts]

    return APIResponse[list[PostResponse]](
        success=True,
        message="Posts fetched successfully",
        status_code=status.HTTP_200_OK,
        data=data,
    )


@router.get(
    "/{post_id}",
    response_model = APIResponse[PostResponse],
    status_code = status.HTTP_200_OK
)
def get_post(
   post_id :  int,
   db : Session = Depends(get_db)
):
    statement = select(Post).where(Post.id == post_id)
    post = db.execute(statement).scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found."
        )

    return APIResponse[PostResponse](
        success=True,
        message="Post fetched successfully",
        status_code=status.HTTP_200_OK,
        data=PostResponse.model_validate(post),
    )


@router.patch(
        "/{post_id}",
        response_model=APIResponse[PostResponse],
        status_code=status.HTTP_200_OK
)
def update_post(
    post_id : int,
    post_data : PostUpdate,
    db : Session = Depends(get_db),
    current_user_id : int = Depends(get_current_user_id)
):
    statement = select(Post).where(Post.id == post_id)
    post = db.execute(statement).scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The post you are trying to update is not exist."
        )

    if post.user_id != current_user_id:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to update this post."
            )

    update_data = post_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    for key, values in update_data.items():
        setattr(post , key , values)

    db.commit()
    db.refresh(post)

    return APIResponse[PostResponse](
                success=True,
                message="Post updated successfully",
                status_code=status.HTTP_200_OK,
                data=PostResponse.model_validate(post)
            )



@router.delete(
    "/{post_id}",
    response_model=APIResponse[None],
    status_code = status.HTTP_200_OK
)
def delete_post(
    post_id : int,
    db : Session = Depends(get_db),
    current_user_id : int = Depends(get_current_user_id)
):
    statement = select(Post).where(Post.id == post_id)
    post = db.execute(statement).scalars().first()

    if not post:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post not found"
    )

    if post.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete this post"
        )

    db.delete(post)
    db.commit()

    return APIResponse[None](
            success=True,
            message="Post deleted successfully",
            status_code=status.HTTP_200_OK,
            data=None
        )

