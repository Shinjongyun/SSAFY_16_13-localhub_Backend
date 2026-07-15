from enum import Enum

from pydantic import BaseModel, Field


class ChatIntent(str, Enum):
    PLACE_RECOMMEND = "PLACE_RECOMMEND"
    FOLLOW_UP = "FOLLOW_UP"
    REGIONAL_INFO = "REGIONAL_INFO"
    UNKNOWN = "UNKNOWN"


class ChatCategory(str, Enum):
    ATTRACTION = "ATTRACTION"
    CULTURE = "CULTURE"
    LEISURE = "LEISURE"
    SHOPPING = "SHOPPING"
    ACCOMMODATION = "ACCOMMODATION"
    FESTIVAL = "FESTIVAL"


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=500
    )

    previousResponseId: str | None = None


class ChatAnalysis(BaseModel):
    intent: ChatIntent

    category: ChatCategory | None = None

    district: str | None = None

    keywords: list[str] = Field(
        default_factory=list
    )


class ChatPlaceItem(BaseModel):
    contentId: str | None = None

    category: ChatCategory

    title: str

    addr1: str | None = None

    addr2: str | None = None

    firstimage: str | None = None


class ChatData(BaseModel):
    answer: str

    places: list[ChatPlaceItem]

    responseId: str | None = None


class ChatResponse(BaseModel):
    success: bool

    status: int

    message: str

    data: ChatData