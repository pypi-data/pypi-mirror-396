from typing import List, Optional, Union

from pydantic import BaseModel, Field


class Info(BaseModel):
    year: Union[str, int, None] = Field(default=None)
    version: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    contributor: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)
    date_created: Optional[str] = Field(default=None)


class Image(BaseModel):
    id: int
    file_name: str
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    license: Optional[int] = Field(default=None)
    flickr_url: Optional[str] = Field(default=None)
    coco_url: Optional[str] = Field(default=None)
    date_captured: Optional[str] = Field(default=None)


class License(BaseModel):
    id: int
    name: str
    url: Optional[str] = Field(default=None)


class Category(BaseModel):
    id: int
    name: str
    keypoints: Optional[List[str]] = Field(default=None)
    skeleton: Optional[List[List[int]]] = Field(default=None)
    supercategory: Optional[str] = Field(default=None)


class SegmentationRleIn(BaseModel):
    size: list[int]
    counts: Union[str, list[int]]


class Annotation(BaseModel):
    id: int
    image_id: int
    category_id: int
    bbox: List[Union[int, float]]
    segmentation: Union[List[List[Union[int, float]]], SegmentationRleIn, None] = Field(
        default=None
    )
    keypoints: Optional[List[Union[int, float]]] = Field(default=None)
    num_keypoints: Optional[int] = Field(default=None)
    score: float = Field(default=0.0)
    iscrowd: int = Field(default=0)
    area: float = Field(default=0.0)
    utf8_string: Optional[str] = None

    def bbox_area(self) -> float:
        if self.bbox is None or self.bbox == []:
            raise ValueError("This annotation has no bbox, so it does not have area")
        if len(self.bbox) != 4:
            raise ValueError(
                f"This annotation has a malformed bbox: {self.bbox} should have a length of 4"
            )
        return self.bbox[2] * self.bbox[3]

    def is_rle(self) -> bool:
        return (
            self.segmentation is not None
            and isinstance(self.segmentation, SegmentationRleIn)
            and self.segmentation != {}
        )

    def is_keypoints(self):
        return (
            self.keypoints is not None
            and isinstance(self.keypoints, List)
            and self.keypoints != []
        )

    def is_polygon(self) -> bool:
        return (
            not self.is_keypoints()
            and not self.is_rle()
            and self.segmentation is not None
            and isinstance(self.segmentation, List)
            and self.segmentation != []
        )

    def is_rectangle(self) -> bool:
        return (
            not self.is_keypoints()
            and not self.is_rle()
            and not self.is_polygon()
            and (
                self.segmentation is None
                or self.segmentation == {}
                or self.segmentation == []
            )
            and not self.bbox == []
        )

    def polygon_to_list_coordinates(self) -> List[List[List[int]]]:
        if not self.is_polygon():
            raise ValueError("This is not a polygon")

        k = 0
        polygons = []
        for polygon in self.segmentation:
            if len(polygon) % 2 != 0:
                raise ValueError(
                    f"The {k} element of this segmentation is not a polygon."
                )
            polygons.append(
                [
                    [int(polygon[k]), int(polygon[k + 1])]
                    for k in range(0, len(polygon), 2)
                ]
            )
            k += 1

        return polygons


class COCOFile(BaseModel):
    info: Info = Field(default_factory=Info)
    licenses: List[License] = Field(default_factory=list)
    categories: List[Category] = Field(default_factory=list)
    images: List[Image]
    annotations: List[Annotation]
