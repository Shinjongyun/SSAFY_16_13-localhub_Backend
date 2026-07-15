from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import Base, engine
from app.models.post import Post
from app.routers.map_router import router as map_router
from app.routers.post_router import router as post_router


# 등록된 SQLAlchemy 모델을 기반으로 테이블 생성
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="LocalHub API",
    version="1.0.0",
)


# 프론트엔드 서버의 API 요청 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# HTTP 예외 처리
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


# 헬스 체크 API
@app.get("/")
def health_check() -> dict[str, str]:
    return {
        "message": "LocalHub 서버가 정상적으로 실행 중입니다."
    }


# 라우터 등록
app.include_router(post_router)
app.include_router(map_router)