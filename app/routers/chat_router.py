# app/routers/chat_router.py

from fastapi import APIRouter

from app.schemas.chat_schema import (
    ChatRequest,
    ChatResponse,
)
from app.services.chat_service import (
    chat_service,
)


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
    summary="서울 지역 정보 챗봇",
)
def chat(
    request: ChatRequest,
) -> ChatResponse:
    return chat_service.chat(
        message=request.message,
        previous_response_id=request.previousResponseId,
    )