from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict
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


class PostResponse(CamelCaseModel):
    id: int
    title: str
    category: Category
    created_at: datetime
    updated_at: datetime


class PostListData(CamelCaseModel):
    post_list: list[PostResponse]


class PostListResponse(CamelCaseModel):
    success: bool
    status: int
    message: str
    data: PostListData