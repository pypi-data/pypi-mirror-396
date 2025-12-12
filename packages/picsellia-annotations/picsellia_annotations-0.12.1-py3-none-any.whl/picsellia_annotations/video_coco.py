from typing import List, Optional

from pydantic import BaseModel, Field

from .coco import Annotation, COCOFile, Image


class ExtendedImage(Image):
    video_id: Optional[int] = Field(default=None)
    frame_id: Optional[int] = Field(default=None)
    file_name: Optional[str] = Field(default=None)


class Video(BaseModel):
    id: int
    file_name: str


class Attributes(BaseModel):
    occluded: bool = Field(default=False)
    rotation: Optional[float] = Field(default=None)
    track_id: Optional[int] = Field(default=None)
    keyframe: bool = Field(default=False)
    frame_id: Optional[int] = Field(default=None)


class VideoAnnotation(Annotation):
    video_id: Optional[int] = Field(default=None)
    attributes: Optional[Attributes] = Field(default=None)


class VideoCOCOFile(COCOFile):
    videos: Optional[List[Video]] = Field(default=None)
    images: List[ExtendedImage]
    annotations: List[VideoAnnotation]
