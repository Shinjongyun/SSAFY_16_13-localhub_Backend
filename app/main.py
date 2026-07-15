from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
from typing import Any

from app.database import Base, engine
from app.models.post import Post
from app.routers.post_router import router as post_router


# 등록된 SQLAlchemy 모델을 바탕으로 테이블 생성
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="LocalHub API",
    version="1.0.0",
)

# 예외 처리기
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status": exc.status_code,
            "message": str(exc.detail),
            "timestamp": datetime.now().isoformat(
                timespec="microseconds",
            ),
        },
    )


# 헬스 체크 용 api
@app.get("/")
def health_check() -> dict[str, str]:
    return {
        "message": "LocalHub 서버가 정상적으로 실행 중입니다."
    }


app.include_router(post_router)