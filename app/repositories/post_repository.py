from datetime import datetime

from app.schemas.post_schema import Category, PostResponse


posts: list[PostResponse] = [
    PostResponse(
        id=1,
        title="서울에서 가볼 만한 관광지 추천",
        category=Category.ATTRACTION,
        created_at=datetime(2026, 7, 14, 15, 30),
        updated_at=datetime(2026, 7, 14, 16, 10),
    ),
    PostResponse(
        id=2,
        title="여름에 즐기기 좋은 수상 레포츠",
        category=Category.LEISURE,
        created_at=datetime(2026, 7, 13, 12, 20),
        updated_at=datetime(2026, 7, 13, 12, 20),
    ),
    PostResponse(
        id=3,
        title="부산 숙박시설 추천",
        category=Category.ACCOMMODATION,
        created_at=datetime(2026, 7, 12, 18, 0),
        updated_at=datetime(2026, 7, 12, 19, 30),
    ),
]


def find_all() -> list[PostResponse]:
    return posts.copy()