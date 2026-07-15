from pydantic import BaseModel, ConfigDict, Field


class MapItem(BaseModel):
    content_id: int = Field(
        serialization_alias="contentId"
    )

    map_x: str = Field(
        serialization_alias="maX"
    )

    map_y: str = Field(
        serialization_alias="maY"
    )

    model_config = ConfigDict(
        populate_by_name=True
    )


class MapData(BaseModel):
    map_list: list[MapItem] = Field(
        serialization_alias="mapList"
    )

    model_config = ConfigDict(
        populate_by_name=True
    )


class MapResponse(BaseModel):
    success: bool
    status: int
    message: str
    data: MapData