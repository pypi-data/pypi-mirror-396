from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict, override


class VideoDict(TypedDict):
    video_id: str
    title: str
    channel_name: str
    published_timestamp: datetime
    short: bool
    duration: int
    progress: int
    watch_timestamp: datetime | None


class VideosResponse(TypedDict):
    videos: list[VideoDict]


@dataclass
class Video:
    video_id: str
    title: str
    channel_name: str
    published_timestamp: datetime
    short: bool
    duration: int
    progress: int
    watch_timestamp: datetime | None = None

    @override
    def __str__(self) -> str:
        return f"{self.channel_name} - {self.title} - {self.video_id}"


@dataclass
class Channel:
    channel_id: str
    name: str

    @override
    def __str__(self) -> str:
        return f"{self.name} - {self.channel_id}"
