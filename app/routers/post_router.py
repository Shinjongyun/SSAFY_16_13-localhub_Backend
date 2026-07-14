from fastapi import APIRouter, HTTPException, status

from app.schemas.post_schema import (
    Category,
    PostDetailResponse,
    PostListResponse,
)
from app.services import post_service


router = APIRouter(
    prefix="/api/posts",
    tags=["posts"],
)


# 전체 게시글 조회
@router.get(
    "",
    response_model=PostListResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
)
def get_posts() -> PostListResponse:
    return post_service.get_posts()


# 카테고리별 게시글 조회
@router.get(
    "/category/{category}",
    response_model=PostListResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
)
def get_posts_by_category(
    category: Category,
) -> PostListResponse:
    return post_service.get_posts_by_category(category)


# 게시글 상세 조회
@router.get(
    "/{post_id}",
    response_model=PostDetailResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
)
def get_post(
    post_id: int,
) -> PostDetailResponse:
    response = post_service.get_post(post_id)

    if response is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다.",
        )

    return response