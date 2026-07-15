from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.map_model import TourismInfo
from app.schemas.chat_schema import (
    ChatCategory,
    ChatPlaceItem,
)


# FE ↔ BE에서는 영어 카테고리를 사용하고,
# DB 조회 시에는 한글 content_type으로 변환한다.
CATEGORY_CONTENT_TYPE_MAP = {
    ChatCategory.ATTRACTION: "관광지",
    ChatCategory.CULTURE: "문화시설",
    ChatCategory.LEISURE: "레포츠",
    ChatCategory.SHOPPING: "쇼핑",
    ChatCategory.ACCOMMODATION: "숙박",
    ChatCategory.FESTIVAL: "축제공연행사",
}


class ChatRepository:

    def search_places(
        self,
        db: Session,
        category: ChatCategory,
        district: str | None,
        keywords: list[str],
        limit: int = 5,
    ) -> list[ChatPlaceItem]:

        content_type = CATEGORY_CONTENT_TYPE_MAP.get(
            category
        )

        if content_type is None:
            return []

        statement = (
            select(TourismInfo)
            .where(
                TourismInfo.content_type == content_type
            )
            .order_by(
                TourismInfo.id.asc()
            )
        )

        result = db.execute(
            statement
        )

        items = list(
            result.scalars().all()
        )

        results: list[
            tuple[int, ChatPlaceItem]
        ] = []

        for item in items:

            title = str(
                item.title or ""
            )

            addr1 = str(
                item.addr1 or ""
            )

            addr2 = str(
                item.addr2 or ""
            )

            search_text = (
                title
                + " "
                + addr1
                + " "
                + addr2
            ).lower()

            # district가 있으면 주소에 포함되어야 함
            if district:

                if district.lower() not in search_text:
                    continue

            score = 0

            for keyword in keywords:

                if keyword.lower() in search_text:
                    score += 1

            # keyword가 있는데 하나도 안 맞으면 제외
            if keywords and score == 0:
                continue

            results.append(
                (
                    score,
                    ChatPlaceItem(
                        contentId=(
                            str(item.content_id)
                            if item.content_id is not None
                            else None
                        ),
                        category=category,
                        title=title,
                        addr1=addr1 or None,
                        addr2=addr2 or None,
                        firstimage=item.firstimage or None,
                    ),
                )
            )

        results.sort(
            key=lambda x: x[0],
            reverse=True,
        )

        return [
            item
            for _, item in results[:limit]
        ]


chat_repository = ChatRepository()