from fastapi import FastAPI

from app.routers.post_router import router as post_router
from app.routers.map_router import router as map_router


app = FastAPI(
    title="LocalHub API",
    version="1.0.0",
)


@app.get("/")
def health_check() -> dict[str, str]:
    return {
        "message": "LocalHub 서버가 정상적으로 실행 중입니다."
    }


app.include_router(post_router)
app.include_router(map_router)