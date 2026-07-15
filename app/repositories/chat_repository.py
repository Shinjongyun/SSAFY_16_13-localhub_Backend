import json
from pathlib import Path
from typing import Any

from app.schemas.chat_schema import (
    ChatCategory,
    ChatPlaceItem,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"


CATEGORY_FILE_MAP = {
    ChatCategory.ATTRACTION: "서울_관광지.json",
    ChatCategory.CULTURE: "서울_문화시설.json",
    ChatCategory.LEISURE: "서울_레포츠.json",
    ChatCategory.SHOPPING: "서울_쇼핑.json",
    ChatCategory.ACCOMMODATION: "서울_숙박.json",
    ChatCategory.FESTIVAL: "서울_축제공연행사.json",
}


class ChatRepository:

    def __init__(self):
        self.cache = self._load_json()

    def _load_json(self):

        cache = {}

        for category, filename in CATEGORY_FILE_MAP.items():

            path = DATA_DIR / filename

            if not path.exists():
                cache[category] = []
                continue

            with open(
                path,
                encoding="utf-8"
            ) as file:

                json_data = json.load(file)

            cache[category] = json_data.get(
                "items",
                []
            )

        return cache

    def search_places(
        self,
        category: ChatCategory,
        district: str | None,
        keywords: list[str],
        limit: int = 5,
    ) -> list[ChatPlaceItem]:

        items = self.cache.get(
            category,
            []
        )

        results = []

        for item in items:

            title = str(
                item.get(
                    "title",
                    ""
                )
            )

            addr1 = str(
                item.get(
                    "addr1",
                    ""
                )
            )

            addr2 = str(
                item.get(
                    "addr2",
                    ""
                )
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
                        contentId=item.get(
                            "contentid"
                        ),
                        category=category,
                        title=title,
                        addr1=addr1 or None,
                        addr2=addr2 or None,
                        firstimage=item.get(
                            "firstimage"
                        ),
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