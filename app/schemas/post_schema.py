from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class Category(str, Enum):
    ATTRACTION = "ATTRACTION"
    LEISURE = "LEISURE"
    CULTURE = "CULTURE"
    SHOPPING = "SHOPPING"
    ACCOMMODATION = "ACCOMMODATION"
    RESTAURANT = "RESTAURANT"
    FESTIVAL = "FESTIVAL"


class CamelCaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


# 게시글 작성 요청
class PostCreateRequest(CamelCaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    category: Category
    password: str = Field(min_length=1, max_length=50)


# 게시글 삭제 요청
class PostDeleteRequest(CamelCaseModel):
    password: str = Field(min_length=1, max_length=50)


# 목록의 게시글 한 개
class PostListItem(CamelCaseModel):
    id: int
    title: str
    category: Category
    created_at: datetime
    updated_at: datetime


class PostListData(CamelCaseModel):
    post_list: list[PostListItem]
    page: int
    size: int
    total_elements: int
    total_pages: int


class PostListResponse(CamelCaseModel):
    success: bool
    status: int
    message: str
    data: PostListData


# 게시글 상세 데이터
class PostDetailData(CamelCaseModel):
    id: int
    title: str
    content: str
    category: Category
    created_at: datetime
    updated_at: datetime


class PostDetailResponse(CamelCaseModel):
    success: bool
    status: int
    message: str
    data: PostDetailData


# 게시글 작성·삭제 응답
class PostActionResponse(CamelCaseModel):
    success: bool
    status: int
    message: str
    data: None = None

class PostUpdateRequest(CamelCaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    category: Category
    password: str = Field(min_length=1, max_length=50)