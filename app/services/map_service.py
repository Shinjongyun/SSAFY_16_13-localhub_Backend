import os
from typing import Any
from urllib.parse import unquote

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.map_model import TourismInfo
from app.repositories.map_repository import map_repository
from app.schemas.map_schema import (
    MapData,
    MapDetailData,
    MapDetailResponse,
    MapItem,
    MapResponse
)


load_dotenv()


DETAIL_COMMON_API_URL = (
    "https://apis.data.go.kr/B551011/KorService2/detailCommon2"
)

MOBILE_OS = "ETC"
MOBILE_APP = "LocalHub"


ALLOWED_CATEGORIES = {
    "관광지",
    "문화시설",
    "축제공연행사",
    "레포츠",
    "숙박",
    "쇼핑"
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

    def get_map_detail(
        self,
        db: Session,
        content_id: int
    ) -> MapDetailResponse:
        tourism_info = self._find_by_content_id(
            db=db,
            content_id=content_id
        )

        if tourism_info is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "해당 관광 정보를 찾을 수 없습니다.",
                    "data": {
                        "contentId": content_id
                    }
                }
            )

        api_item = self._request_detail_api(
            content_id=content_id
        )

        return MapDetailResponse(
            success=True,
            status=200,
            message="요청에 성공하였습니다.",
            data=MapDetailData(
                title=self._to_string(
                    api_item.get("title")
                ),
                first_image=self._empty_to_none(
                    api_item.get("firstimage")
                ),
                addr1=self._empty_to_none(
                    api_item.get("addr1")
                ),
                addr2=self._empty_to_none(
                    api_item.get("addr2")
                ),
                overview=self._empty_to_none(
                    api_item.get("overview")
                )
            )
        )

    def _find_by_content_id(
        self,
        db: Session,
        content_id: int
    ) -> TourismInfo | None:
        try:
            return map_repository.find_by_content_id(
                db=db,
                content_id=content_id
            )

        except SQLAlchemyError as error:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "관광 정보를 조회하는 중 오류가 발생했습니다.",
                    "data": {
                        "reason": str(error)
                    }
                }
            ) from error

    def _request_detail_api(
        self,
        content_id: int
    ) -> dict[str, Any]:
        service_key = os.getenv(
            "TOUR_API_SERVICE_KEY"
        )

        if not service_key:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "관광 API 인증키가 설정되지 않았습니다.",
                    "data": None
                }
            )

        decoded_service_key = unquote(
            service_key.strip()
        )

        params = {
            "serviceKey": decoded_service_key,
            "MobileOS": MOBILE_OS,
            "MobileApp": MOBILE_APP,
            "_type": "json",
            "contentId": content_id,
            "numOfRows": 10,
            "pageNo": 1
        }

        try:
            with httpx.Client(
                timeout=10.0
            ) as client:
                response = client.get(
                    DETAIL_COMMON_API_URL,
                    params=params
                )

                response.raise_for_status()

        except httpx.TimeoutException as error:
            raise HTTPException(
                status_code=504,
                detail={
                    "message": "관광 정보 API 응답 시간이 초과되었습니다.",
                    "data": None
                }
            ) from error

        except httpx.HTTPStatusError as error:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "관광 정보 API 호출에 실패했습니다.",
                    "data": {
                        "apiStatus": error.response.status_code,
                        "apiResponse": error.response.text
                    }
                }
            ) from error

        except httpx.RequestError as error:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "관광 정보 API에 연결할 수 없습니다.",
                    "data": {
                        "reason": str(error)
                    }
                }
            ) from error

        try:
            response_data = response.json()

        except ValueError as error:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "관광 정보 API 응답이 JSON 형식이 아닙니다.",
                    "data": {
                        "apiResponse": response.text
                    }
                }
            ) from error

        return self._parse_detail_response(
            response_data=response_data,
            content_id=content_id
        )

    def _parse_detail_response(
        self,
        response_data: dict[str, Any],
        content_id: int
    ) -> dict[str, Any]:
        if "response" not in response_data:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "관광 정보 API가 오류를 반환했습니다.",
                    "data": {
                        "resultCode": response_data.get(
                            "resultCode"
                        ),
                        "resultMessage": response_data.get(
                            "resultMsg"
                        )
                    }
                }
            )

        api_response = response_data.get("response")

        if not isinstance(api_response, dict):
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "관광 정보 API 응답 구조가 올바르지 않습니다.",
                    "data": {
                        "apiResponse": response_data
                    }
                }
            )

        header = api_response.get("header")

        if not isinstance(header, dict):
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "관광 정보 API 응답 헤더가 존재하지 않습니다.",
                    "data": {
                        "apiResponse": response_data
                    }
                }
            )

        result_code = str(
            header.get("resultCode", "")
        )

        if result_code not in {"0000", "00"}:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "관광 정보 API가 오류를 반환했습니다.",
                    "data": {
                        "resultCode": result_code,
                        "resultMessage": header.get(
                            "resultMsg"
                        )
                    }
                }
            )

        body = api_response.get("body")

        if not isinstance(body, dict):
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "관광 정보 API 응답 본문이 존재하지 않습니다.",
                    "data": {
                        "apiResponse": response_data
                    }
                }
            )

        items = body.get("items")

        if not isinstance(items, dict):
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "관광 상세 정보를 찾을 수 없습니다.",
                    "data": {
                        "contentId": content_id
                    }
                }
            )

        item = items.get("item")

        if isinstance(item, list):
            if not item:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "message": "관광 상세 정보를 찾을 수 없습니다.",
                        "data": {
                            "contentId": content_id
                        }
                    }
                )

            first_item = item[0]

            if not isinstance(first_item, dict):
                raise HTTPException(
                    status_code=502,
                    detail={
                        "message": "관광 상세 정보 형식이 올바르지 않습니다.",
                        "data": None
                    }
                )

            return first_item

        if isinstance(item, dict):
            return item

        raise HTTPException(
            status_code=404,
            detail={
                "message": "관광 상세 정보를 찾을 수 없습니다.",
                "data": {
                    "contentId": content_id
                }
            }
        )

    @staticmethod
    def _empty_to_none(
        value: Any
    ) -> str | None:
        if value is None:
            return None

        string_value = str(value).strip()

        return string_value or None

    @staticmethod
    def _to_string(
        value: Any
    ) -> str:
        if value is None:
            return ""

        return str(value).strip()


map_service = MapService()