from dataclasses import dataclass
from enum import IntEnum
from typing import Optional


class EnumGroupType(IntEnum) :
    Translation = 0
    Transfer = 1
    Compression = 2


class EnumLanguage(IntEnum) :
    JpSc = 0
    ScTc = 1
    JpScTc = 2
    Sc = 3
    JpTc = 4
    Tc = 5
    Jp = 6
    Unspecified = 7
    Eng = 8
    EngSc = 9
    EngTc = 10
    EngScTc = 11


class EnumMediaType(IntEnum) :
    SingleEpisode = 0
    MultipleEpisode = 1
    Movie = 2
    Ova = 3


class EnumResolution(IntEnum) :
    R480p = 0
    R720p = 1
    R1080p = 2
    R2K = 3
    R4K = 4
    Unknown = 5


class EnumSubtitleType(IntEnum) :
    Embedded = 0
    Muxed = 1
    External = 2
    Unspecified = 3


@dataclass
class ParseResult :
    title: str
    episode: Optional[float]
    version: int
    start_episode: Optional[int]
    end_episode: Optional[int]
    group: str
    group_type: EnumGroupType
    language: EnumLanguage
    subtitle_type: EnumSubtitleType
    resolution: EnumResolution
    source: str
    web_source: str
    media_type: EnumMediaType


def from_json(d: dict) -> ParseResult :
    """把 JSON dict 转换为 ParseResult"""
    return ParseResult(
            title = d["Title"],
            episode = d.get("Episode"),
            version = d.get("Version", 1),
            start_episode = None,
            end_episode = None,
            group = d.get("Group", ""),
            group_type = EnumGroupType(d["GroupType"]),
            language = EnumLanguage(d["Language"]),
            subtitle_type = EnumSubtitleType(d["SubtitleType"]),
            resolution = EnumResolution(d["Resolution"]),
            source = d.get("Source", ""),
            web_source = d.get("WebSource", ""),
            media_type = EnumMediaType(d["MediaType"]),
    )
