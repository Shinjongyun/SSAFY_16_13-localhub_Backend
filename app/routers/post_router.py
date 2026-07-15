from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.post_schema import (
    Category,
    PostActionResponse,
    PostCreateRequest,
    PostDeleteRequest,
    PostDetailResponse,
    PostListResponse,
    PostUpdateRequest,
)
from app.services import post_service


router = APIRouter(
    prefix="/api/posts",
    tags=["posts"],
)


# 전체 게시글 조회
@router.get(
    "/all",
    response_model=PostListResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
)
def get_posts(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
) -> PostListResponse:
    return post_service.get_posts(
        page=page,
        size=size,
    )


# 게시글 작성
@router.post(
    "",
    response_model=PostActionResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
)
def create_post(
    request: PostCreateRequest,
) -> PostActionResponse:
    return post_service.create_post(request)


# 카테고리별 게시글 조회
@router.get(
    "/category/{category}",
    response_model=PostListResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
)
def get_posts_by_category(
    category: Category,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
) -> PostListResponse:
    return post_service.get_posts_by_category(
        category=category,
        page=page,
        size=size,
    )


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
    try:
        return post_service.get_post(post_id)

    except post_service.PostNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다.",
        )


# 게시글 삭제
@router.delete(
    "/{post_id}",
    response_model=PostActionResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
)
def delete_post(
    post_id: int,
    request: PostDeleteRequest,
) -> PostActionResponse:
    try:
        return post_service.delete_post(post_id, request)

    except post_service.PostNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다.",
        )

    except post_service.InvalidPostPasswordError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비밀번호가 일치하지 않습니다.",
        )
    
# 게시글 수정
@router.put(
    "/{post_id}",
    response_model=PostActionResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
)
def update_post(
    post_id: int,
    request: PostUpdateRequest,
) -> PostActionResponse:
    try:
        return post_service.update_post(post_id, request)

    except post_service.PostNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다.",
        )

    except post_service.InvalidPostPasswordError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비밀번호가 일치하지 않습니다.",
        )