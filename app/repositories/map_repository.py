from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.map_model import TourismInfo


class MapRepository:
    def find_all_by_content_type(
        self,
        db: Session,
        content_type: str
    ) -> list[TourismInfo]:
        statement = (
            select(TourismInfo)
            .where(
                TourismInfo.content_type == content_type,
                TourismInfo.map_x.is_not(None),
                TourismInfo.map_y.is_not(None)
            )
            .order_by(TourismInfo.id.asc())
        )

        result = db.execute(statement)

        return list(result.scalars().all())


map_repository = MapRepository()