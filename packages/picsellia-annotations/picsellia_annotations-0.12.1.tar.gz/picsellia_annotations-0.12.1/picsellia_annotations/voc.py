from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class Size(BaseModel):
    width: int
    height: int
    depth: int


class Source(BaseModel):
    database: str


class BndBox(BaseModel):
    xmin: Union[int, float]
    xmax: Union[int, float]
    ymin: Union[int, float]
    ymax: Union[int, float]


class Object(BaseModel):
    name: str
    pose: Optional[str] = Field(default=None)
    truncated: Optional[int] = Field(default=None)
    difficult: Optional[int] = Field(default=None)
    occluded: Optional[int] = Field(default=None)
    bndbox: Optional[BndBox] = Field(default=None)
    polygon: Optional[Dict[str, Union[int, float]]] = Field(default=None)

    def is_rle(self) -> bool:
        return False

    def is_polygon(self) -> bool:
        return self.polygon is not None

    def is_rectangle(self) -> bool:
        return self.polygon is None and self.bndbox is not None

    def polygon_to_list_coordinates(self) -> List[List[int]]:
        if not self.is_polygon():
            raise ValueError("Not a polygon")

        coords = []
        for i in range(1, 1 + len(self.polygon) // 2):
            x = "x" + str(i)
            y = "y" + str(i)
            if x not in self.polygon or y not in self.polygon:
                raise ValueError("{} or {} not found in this polygon.".format(x, y))

            coords.append([int(self.polygon[x]), int(self.polygon[y])])

        return coords


class Annotation(BaseModel):
    filename: str
    object: Union[Object, List[Object]]
    path: Optional[str] = Field(default=None)
    folder: Optional[str] = Field(default=None)
    source: Optional[Source] = Field(default=None)
    size: Optional[Size] = Field(default=None)
    segmented: Optional[int] = Field(default=None)


class PascalVOCFile(BaseModel):
    annotation: Annotation
