from app.repositories import post_repository
from app.schemas.post_schema import (
    Category,
    PostActionResponse,
    PostCreateRequest,
    PostDeleteRequest,
    PostDetailData,
    PostDetailResponse,
    PostListData,
    PostListItem,
    PostListResponse,
    PostUpdateRequest,
)


class PostNotFoundError(Exception):
    pass


class InvalidPostPasswordError(Exception):
    pass


def get_posts() -> PostListResponse:
    posts = post_repository.find_all()

    return create_post_list_response(posts)


def get_posts_by_category(
    category: Category,
) -> PostListResponse:
    posts = post_repository.find_all_by_category(category)

    return create_post_list_response(posts)


def get_post(post_id: int) -> PostDetailResponse:
    post = post_repository.find_by_id(post_id)

    if post is None:
        raise PostNotFoundError

    return PostDetailResponse(
        success=True,
        status=200,
        message="요청에 성공하였습니다.",
        data=PostDetailData(
            id=post.id,
            title=post.title,
            content=post.content,
            category=post.category,
            created_at=post.created_at,
            updated_at=post.updated_at,
        ),
    )


def create_post(
    request: PostCreateRequest,
) -> PostActionResponse:
    post_repository.save(
        title=request.title,
        content=request.content,
        category=request.category,
        password=request.password,
    )

    return create_success_response()


def delete_post(
    post_id: int,
    request: PostDeleteRequest,
) -> PostActionResponse:
    post = post_repository.find_by_id(post_id)

    if post is None:
        raise PostNotFoundError

    if post.password != request.password:
        raise InvalidPostPasswordError

    post_repository.delete_by_id(post_id)

    return create_success_response()


def create_post_list_response(
    posts: list[post_repository.Post],
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


def create_success_response() -> PostActionResponse:
    return PostActionResponse(
        success=True,
        status=200,
        message="요청에 성공하였습니다.",
        data=None,
    )

def update_post(
    post_id: int,
    request: PostUpdateRequest,
) -> PostActionResponse:
    post = post_repository.find_by_id(post_id)

    if post is None:
        raise PostNotFoundError

    if post.password != request.password:
        raise InvalidPostPasswordError

    post_repository.update_by_id(
        post_id=post_id,
        title=request.title,
        content=request.content,
        category=request.category,
    )

    return create_success_response()