import json
import logging
import os
import xml.etree.ElementTree as ET

import xmltodict

from picsellia_annotations.coco import COCOFile
from picsellia_annotations.exceptions import FileError, ParsingError
from picsellia_annotations.video_coco import VideoCOCOFile
from picsellia_annotations.voc import PascalVOCFile

logger = logging.getLogger("picsellia-annotations")


def _read_file(file_path: str, expected_cls):
    if not os.path.exists(file_path):
        raise FileError("{} was not found".format(file_path))

    logger.debug("Parsing file..")

    try:
        with open(file_path, "r") as f:
            content = json.load(f)
            return expected_cls(**content)
    except Exception as e:
        raise ParsingError(str(e))


def read_coco_file(file_path: str) -> COCOFile:
    return _read_file(file_path, COCOFile)


def read_video_coco_file(file_path: str) -> VideoCOCOFile:
    return _read_file(file_path, VideoCOCOFile)


def write_coco_file(cocofile: COCOFile) -> str:
    try:
        return cocofile.model_dump_json()
    except Exception as e:  # pragma: no cover
        raise ParsingError(str(e))


def read_pascal_voc_file(
    file_path: str, check_polygon_consistency: bool = False
) -> PascalVOCFile:
    if not os.path.exists(file_path):
        raise FileError("{} was not found".format(file_path))

    logger.debug("Parsing file {}".format(file_path))

    try:
        tree = ET.parse(file_path)
        xmlstr = ET.tostring(tree.getroot(), encoding="utf-8", method="xml")
        content = xmltodict.parse(xmlstr)
        vocfile = PascalVOCFile(**content)

        # This will raises an error if polygon is not consistent
        if check_polygon_consistency:
            vocfile.annotation.object.polygon_to_list_coordinates()

    except Exception as e:
        raise ParsingError(str(e))

    return vocfile


def write_pascal_voc_file(
    voc: PascalVOCFile, output=None, pretty: bool = True, full_document: bool = False
) -> str:
    try:
        xmlstr = xmltodict.unparse(
            voc.model_dump(), output=output, full_document=full_document, pretty=pretty
        )
    except Exception as e:  # pragma: no cover
        raise ParsingError(str(e))

    return xmlstr
