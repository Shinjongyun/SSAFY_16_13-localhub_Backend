from datetime import datetime

from app.schemas.post_schema import Category, PostDetailData


posts: list[PostDetailData] = [
    PostDetailData(
        id=1,
        title="서울에서 가볼 만한 관광지 추천",
        content="경복궁과 북촌한옥마을을 추천합니다.",
        category=Category.ATTRACTION,
        created_at=datetime(2026, 7, 14, 15, 30),
        updated_at=datetime(2026, 7, 14, 16, 10),
    ),
    PostDetailData(
        id=2,
        title="여름에 즐기기 좋은 수상 레포츠",
        content="한강에서 카약과 패들보드를 즐길 수 있습니다.",
        category=Category.LEISURE,
        created_at=datetime(2026, 7, 13, 12, 20),
        updated_at=datetime(2026, 7, 13, 12, 20),
    ),
    PostDetailData(
        id=3,
        title="부산 숙박시설 추천",
        content="해운대 주변의 숙박시설을 추천합니다.",
        category=Category.ACCOMMODATION,
        created_at=datetime(2026, 7, 12, 18, 0),
        updated_at=datetime(2026, 7, 12, 19, 30),
    ),
]


def find_all() -> list[PostDetailData]:
    return posts.copy()


def find_all_by_category(
    category: Category,
) -> list[PostDetailData]:
    return [
        post
        for post in posts
        if post.category == category
    ]


def find_by_id(
    post_id: int,
) -> PostDetailData | None:
    for post in posts:
        if post.id == post_id:
            return post

    return None