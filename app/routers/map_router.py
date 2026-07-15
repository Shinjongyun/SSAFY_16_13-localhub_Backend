from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.map_schema import (
    MapDetailResponse,
    MapResponse
)
from app.services.map_service import map_service


router = APIRouter(
    prefix="/api/maps",
    tags=["Map"]
)


@router.get(
    "",
    response_model=MapResponse,
    response_model_by_alias=True,
    summary="카테고리별 지도 정보 조회"
)
def get_maps_by_category(
    category: Annotated[
        str,
        Query(
            description="조회할 관광 정보 카테고리",
            examples=["관광지"]
        )
    ],
    db: Session = Depends(get_db)
) -> MapResponse:
    return map_service.get_maps_by_category(
        db=db,
        category=category
    )


@router.get(
    "/{contentId}",
    response_model=MapDetailResponse,
    response_model_by_alias=True,
    summary="관광 정보 상세 조회"
)
def get_map_detail(
    contentId: Annotated[
        int,
        Path(
            description="조회할 관광 정보의 contentId",
            examples=[126128],
            gt=0
        )
    ],
    db: Session = Depends(get_db)
) -> MapDetailResponse:
    return map_service.get_map_detail(
        db=db,
        content_id=contentId
    )