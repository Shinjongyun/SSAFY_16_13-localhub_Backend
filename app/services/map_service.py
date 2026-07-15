from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.repositories.map_repository import map_repository
from app.schemas.map_schema import MapData, MapItem, MapResponse


ALLOWED_CATEGORIES = {
    "관광지",
    "문화시설",
    "축제공연행사",
    "여행코스",
    "레포츠",
    "숙박",
    "쇼핑",
    "음식점"
}


class MapService:
    def get_maps_by_category(
        self,
        db: Session,
        category: str
    ) -> MapResponse:
        normalized_category = category.strip()

        if normalized_category not in ALLOWED_CATEGORIES:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "지원하지 않는 카테고리입니다.",
                    "data": {
                        "category": normalized_category,
                        "availableCategories": sorted(
                            ALLOWED_CATEGORIES
                        )
                    }
                }
            )

        try:
            tourism_infos = (
                map_repository.find_all_by_content_type(
                    db=db,
                    content_type=normalized_category
                )
            )

        except SQLAlchemyError as error:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "지도 정보를 조회하는 중 오류가 발생했습니다.",
                    "data": {
                        "reason": str(error)
                    }
                }
            ) from error

        map_list = [
            MapItem(
                content_id=tourism_info.content_id,
                map_x=str(tourism_info.map_x),
                map_y=str(tourism_info.map_y)
            )
            for tourism_info in tourism_infos
        ]

        return MapResponse(
            success=True,
            status=200,
            message="요청에 성공하였습니다.",
            data=MapData(
                map_list=map_list
            )
        )


map_service = MapService()