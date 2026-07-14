from app.repositories import post_repository
from app.schemas.post_schema import PostListData, PostListResponse


def get_posts() -> PostListResponse:
    posts = post_repository.find_all()

    return PostListResponse(
        success=True,
        status=200,
        message="요청에 성공하였습니다.",
        data=PostListData(
            post_list=posts,
        ),
    )