from datetime import datetime

from sqlalchemy import func, select

from app.database import SessionLocal
from app.models.post import Post
from app.schemas.post_schema import Category


def find_all(
    page: int,
    size: int,
) -> tuple[list[Post], int]:
    offset = (page - 1) * size

    with SessionLocal() as db:
        total_elements = db.scalar(
            select(func.count(Post.id))
        ) or 0

        statement = (
            select(Post)
            .order_by(Post.id.asc())
            .offset(offset)
            .limit(size)
        )

        posts = list(
            db.scalars(statement).all()
        )

        return posts, total_elements


def find_all_by_category(
    category: Category,
    page: int,
    size: int,
) -> tuple[list[Post], int]:
    offset = (page - 1) * size

    with SessionLocal() as db:
        total_elements = db.scalar(
            select(func.count(Post.id))
            .where(Post.category == category)
        ) or 0

        statement = (
            select(Post)
            .where(Post.category == category)
            .order_by(Post.id.asc())
            .offset(offset)
            .limit(size)
        )

        posts = list(
            db.scalars(statement).all()
        )

        return posts, total_elements


def find_by_id(
    post_id: int,
) -> Post | None:
    with SessionLocal() as db:
        return db.get(Post, post_id)


def save(
    title: str,
    content: str,
    category: Category,
    password: str,
) -> Post:
    with SessionLocal() as db:
        now = datetime.now()

        post = Post(
            title=title,
            content=content,
            category=category,
            password=password,
            created_at=now,
            updated_at=now,
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        return post


def delete_by_id(
    post_id: int,
) -> bool:
    with SessionLocal() as db:
        post = db.get(Post, post_id)

        if post is None:
            return False

        db.delete(post)
        db.commit()

        return True


def update_by_id(
    post_id: int,
    title: str,
    content: str,
    category: Category,
) -> Post | None:
    with SessionLocal() as db:
        post = db.get(Post, post_id)

        if post is None:
            return None

        post.title = title
        post.content = content
        post.category = category
        post.updated_at = datetime.now()

        db.commit()
        db.refresh(post)

        return post