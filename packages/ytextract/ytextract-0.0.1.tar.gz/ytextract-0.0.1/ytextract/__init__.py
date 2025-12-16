# flake8: noqa: F401
# noreorder
"""
ytextract: a very serious Python library for downloading YouTube Videos.
"""
from importlib.metadata import version, PackageNotFoundError

__title__ = "ytextract"
__author__ = "Josh-XT"
__license__ = "The Unlicense (Unlicense)"
__js__ = None
__js_url__ = None

try:
    __version__ = version("ytextract")
except PackageNotFoundError:
    __version__ = "0.0.1"  # fallback for development

from ytextract.streams import Stream
from ytextract.captions import Caption
from ytextract.query import CaptionQuery, StreamQuery
from ytextract.__main__ import YouTube
from ytextract.innertube import InnerTube
from ytextract.download_helper import (
    download_video,
    download_videos_from_channels,
    download_videos_from_list,
    download_captions,
    get_videos_from_channel,
)

download = download_video
