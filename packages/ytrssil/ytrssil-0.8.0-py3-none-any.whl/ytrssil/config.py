import json
import os
from dataclasses import dataclass
from typing import Literal, NotRequired, TypedDict, cast


class ConfigDict(TypedDict):
    token: str
    api_url: NotRequired[str]
    max_resolution: NotRequired[Literal["480", "720", "1080", "1440", "2160"]]


@dataclass
class Configuration:
    token: str
    api_url: str = "https://ytrssil.theedgeofrage.com"
    max_resolution: Literal["480", "720", "1080", "1440", "2160"] = "1440"

    @property
    def mpv_options(self) -> list[str]:
        return [
            "--no-terminal",
            (f"--ytdl-format=bestvideo[height<=?{self.max_resolution}]+bestaudio/best"),
        ]


def load_config() -> Configuration:
    config_prefix: str
    try:
        config_prefix = os.environ["XDG_CONFIG_HOME"]
    except KeyError:
        config_prefix = os.path.expanduser("~/.config")

    config_path: str = os.path.join(config_prefix, "ytrssil", "config.json")
    with open(config_path) as f:
        config_data = cast(ConfigDict, json.load(f))

    return Configuration(**config_data)
