from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.chat_schema import (
    ChatRequest,
    ChatResponse,
)
from app.services.chat_service import chat_service


router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:

    return chat_service.chat(
        db=db,
        message=request.message,
        previous_response_id=request.previousResponseId,
    )