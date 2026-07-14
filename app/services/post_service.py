from app.repositories import post_repository
from app.schemas.post_schema import (
    Category,
    PostDetailData,
    PostDetailResponse,
    PostListData,
    PostListItem,
    PostListResponse,
)


def get_posts() -> PostListResponse:
    posts = post_repository.find_all()

    return create_post_list_response(posts)


def get_posts_by_category(
    category: Category,
) -> PostListResponse:
    posts = post_repository.find_all_by_category(category)

    return create_post_list_response(posts)


def get_post(
    post_id: int,
) -> PostDetailResponse | None:
    post = post_repository.find_by_id(post_id)

    if post is None:
        return None

    return PostDetailResponse(
        success=True,
        status=200,
        message="요청에 성공하였습니다.",
        data=post,
    )


def create_post_list_response(
    posts: list[PostDetailData],
) -> PostListResponse:
    post_items = [
        PostListItem(
            id=post.id,
            title=post.title,
            category=post.category,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )
        for post in posts
    ]

    return PostListResponse(
        success=True,
        status=200,
        message="요청에 성공하였습니다.",
        data=PostListData(
            post_list=post_items,
        ),
    )