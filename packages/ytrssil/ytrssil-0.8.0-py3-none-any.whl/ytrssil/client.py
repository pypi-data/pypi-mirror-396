import json
from http.client import HTTPException, HTTPResponse, HTTPSConnection
from typing import cast
from urllib.parse import urlparse

from ytrssil.config import Configuration
from ytrssil.models import Video, VideosResponse


class Client:
    def __init__(self, config: Configuration) -> None:
        parsed = urlparse(config.api_url)
        self.host: str = parsed.netloc
        self.base_path: str = parsed.path.rstrip("/")
        self.token: str = config.token

    def _request(self, method: str, path: str, need_auth: bool = False) -> HTTPResponse:
        conn = HTTPSConnection(self.host)
        headers: dict[str, str] = {}
        if need_auth:
            headers["Authorization"] = self.token

        conn.request(method, f"{self.base_path}{path}", headers=headers)
        resp = conn.getresponse()

        if resp.status >= 400:
            conn.close()
            raise HTTPException(f"HTTP {resp.status} {resp.reason} for {method} {path}")

        return resp

    def fetch(self) -> None:
        resp = self._request("POST", "/fetch")
        resp.close()

    def subscribe_to_channel(self, channel_id: str) -> None:
        resp = self._request("POST", f"/api/channels/{channel_id}/subscribe", True)
        resp.close()

    def get_new_videos(self) -> list[Video]:
        resp = self._request("GET", "/api/videos/new", True)
        body = resp.read()
        resp.close()

        data = cast(VideosResponse, json.loads(body))
        ret: list[Video] = []
        for video_data in data["videos"]:
            ret.append(Video(**video_data))

        return ret

    def get_watched_videos(self) -> list[Video]:
        resp = self._request("GET", "/api/videos/watched", True)
        body = resp.read()
        resp.close()

        data = cast(VideosResponse, json.loads(body))
        ret: list[Video] = []
        for video_data in data["videos"]:
            ret.append(Video(**video_data))

        return ret

    def mark_video_as_watched(self, video_id: str) -> None:
        resp = self._request("POST", f"/api/videos/{video_id}/watch", True)
        resp.close()

    def mark_video_as_unwatched(self, video_id: str) -> None:
        resp = self._request("POST", f"/api/videos/{video_id}/unwatch", True)
        resp.close()
