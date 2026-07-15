from dataclasses import dataclass
from datetime import datetime

from app.schemas.post_schema import Category


@dataclass
class Post:
    id: int
    title: str
    content: str
    category: Category
    password: str
    created_at: datetime
    updated_at: datetime


posts: list[Post] = [
    Post(
        id=1,
        title="서울에서 가볼 만한 관광지 추천",
        content="경복궁과 북촌한옥마을을 추천합니다.",
        category=Category.ATTRACTION,
        password="1234",
        created_at=datetime(2026, 7, 14, 15, 30),
        updated_at=datetime(2026, 7, 14, 16, 10),
    ),
    Post(
        id=2,
        title="여름에 즐기기 좋은 수상 레포츠",
        content="한강에서 카약과 패들보드를 즐길 수 있습니다.",
        category=Category.LEISURE,
        password="1234",
        created_at=datetime(2026, 7, 13, 12, 20),
        updated_at=datetime(2026, 7, 13, 12, 20),
    ),
    Post(
        id=3,
        title="부산 숙박시설 추천",
        content="해운대 주변의 숙박시설을 추천합니다.",
        category=Category.ACCOMMODATION,
        password="1234",
        created_at=datetime(2026, 7, 12, 18, 0),
        updated_at=datetime(2026, 7, 12, 19, 30),
    ),
]

next_id = 4


def find_all(
    page: int,
    size: int,
) -> tuple[list[Post], int]:
    return paginate(posts, page, size)


def find_all_by_category(
    category: Category,
    page: int,
    size: int,
) -> tuple[list[Post], int]:
    category_posts = [
        post
        for post in posts
        if post.category == category
    ]

    return paginate(category_posts, page, size)


def find_by_id(post_id: int) -> Post | None:
    for post in posts:
        if post.id == post_id:
            return post

    return None


def save(
    title: str,
    content: str,
    category: Category,
    password: str,
) -> Post:
    global next_id

    now = datetime.now()

    post = Post(
        id=next_id,
        title=title,
        content=content,
        category=category,
        password=password,
        created_at=now,
        updated_at=now,
    )

    posts.append(post)
    next_id += 1

    return post


def delete_by_id(post_id: int) -> bool:
    for index, post in enumerate(posts):
        if post.id == post_id:
            posts.pop(index)
            return True

    return False

def update_by_id(
    post_id: int,
    title: str,
    content: str,
    category: Category,
) -> Post | None:
    post = find_by_id(post_id)

    if post is None:
        return None

    post.title = title
    post.content = content
    post.category = category
    post.updated_at = datetime.now()

    return post


def paginate(
    target_posts: list[Post],
    page: int,
    size: int,
) -> tuple[list[Post], int]:
    total_elements = len(target_posts)

    start_index = (page - 1) * size
    end_index = start_index + size

    paged_posts = target_posts[start_index:end_index]

    return paged_posts, total_elements