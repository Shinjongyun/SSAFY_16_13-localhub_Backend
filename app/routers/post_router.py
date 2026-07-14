from fastapi import APIRouter, status

from app.schemas.post_schema import PostListResponse
from app.services import post_service


router = APIRouter(
    prefix="/api/posts",
    tags=["posts"],
)


@router.get(
    "",
    response_model=PostListResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
)
def get_posts() -> PostListResponse:
    return post_service.get_posts()