from collections.abc import Iterator
from os import execv, fork
from subprocess import PIPE, Popen
from sys import stderr

from ytrssil.client import Client
from ytrssil.config import Configuration
from ytrssil.models import Video


class CLI:
    config: Configuration
    client: Client

    def __init__(self, config: Configuration, client: Client):
        self.config = config
        self.client = client

    @staticmethod
    def user_query(videos: list[Video], reverse: bool = False) -> list[str]:
        p = Popen(
            ["fzf", "-m"],
            stdout=PIPE,
            stdin=PIPE,
        )
        video_list: Iterator[Video]
        if reverse:
            video_list = reversed(videos)
        else:
            video_list = iter(videos)

        input_bytes = "\n".join(map(str, video_list)).encode("UTF-8")
        stdout, _ = p.communicate(input=input_bytes)
        videos_str: list[str] = stdout.decode("UTF-8").strip().split("\n")
        ret: list[str] = []
        for video_str in videos_str:
            if video_str == "":
                continue

            *_, video_id = video_str.split(" - ")

            try:
                ret.append(video_id)
            except KeyError:
                pass

        return ret

    def fetch(self) -> int:
        self.client.fetch()
        return 0

    def subscribe_to_channel(self, channel_id: str) -> int:
        self.client.subscribe_to_channel(channel_id)
        return 0

    def watch_videos(self) -> int:
        videos = self.client.get_new_videos()
        if not videos:
            print("No new videos", file=stderr)
            return 1

        selected_videos = self.user_query(videos)
        if not selected_videos:
            print("No video selected", file=stderr)
            return 2

        video_urls = [
            f"https://www.youtube.com/watch?v={video_id}"
            for video_id in selected_videos
        ]
        cmd = ["/usr/bin/mpv", *self.config.mpv_options, *video_urls]
        if fork() == 0:
            execv(cmd[0], cmd)

        for video_id in selected_videos:
            self.client.mark_video_as_watched(video_id)

        return 0

    def print_url(self) -> int:
        videos = self.client.get_new_videos()
        if not videos:
            print("No new videos", file=stderr)
            return 1

        selected_videos = self.user_query(videos)
        if not selected_videos:
            print("No video selected", file=stderr)
            return 2

        for video_id in selected_videos:
            self.client.mark_video_as_watched(video_id)
            print(f"https://www.youtube.com/watch?v={video_id}")

        return 0

    def mark_as_watched(self) -> int:
        videos = self.client.get_new_videos()
        if not videos:
            print("No new videos", file=stderr)
            return 1

        selected_videos = self.user_query(videos)
        if not selected_videos:
            print("No video selected", file=stderr)
            return 2

        for video_id in selected_videos:
            self.client.mark_video_as_watched(video_id)

        return 0

    def watch_history(self) -> int:
        videos = self.client.get_watched_videos()
        if not videos:
            print("No new videos", file=stderr)
            return 1

        selected_videos = self.user_query(videos)
        if not selected_videos:
            print("No video selected", file=stderr)
            return 2

        video_urls = [
            f"https://www.youtube.com/watch?v={video_id}"
            for video_id in selected_videos
        ]
        cmd = ["/usr/bin/mpv", *self.config.mpv_options, *video_urls]
        if fork() == 0:
            execv(cmd[0], cmd)

        return 0

    def mark_as_unwatched(self) -> int:
        videos = self.client.get_watched_videos()
        if not videos:
            print("No new videos", file=stderr)
            return 1

        selected_videos = self.user_query(videos)
        if not selected_videos:
            print("No video selected", file=stderr)
            return 2

        for video_id in selected_videos:
            self.client.mark_video_as_unwatched(video_id)

        return 0
