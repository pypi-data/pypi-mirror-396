import os
import re
import sys
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from ytextract import YouTube
from ytextract.innertube import _default_clients


def get_videos_from_channel(channel_name: str = ""):
    if not channel_name:
        return "No channel name provided."
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    url = f"https://www.youtube.com/@{channel_name}"
    driver.get(url)
    time.sleep(5)
    video_elements = driver.find_elements(By.CSS_SELECTOR, "a#video-title")
    video_ids = [
        video.get_attribute("href")
        for video in video_elements
        if video.get_attribute("href")
    ]
    driver.quit()
    return video_ids


def download_video(url: str = "", language: str = "en-US"):
    if not url:
        return "No URL provided."
    os.makedirs("videos", exist_ok=True)
    try:
        yt = YouTube(url)
        video_stream = yt.streams.get_highest_resolution()
        output_video = yt.title.replace(" ", "_")
        output_video = "".join([c for c in output_video if c.isalnum() or c in "._- "])
        video_stream.download(output_path="videos", filename=f"{output_video}.mp4")
    except:
        _default_clients["ANDROID_EMBED"] = _default_clients["MWEB"]
        yt = YouTube(url)
        video_stream = yt.streams.get_highest_resolution()
        output_video = yt.title.replace(" ", "_")
        output_video = "".join([c for c in output_video if c.isalnum() or c in "._- "])
        video_stream.download(output_path="videos", filename=f"{output_video}.mp4")

    video_path = os.path.abspath(f"videos/{output_video}.mp4")
    transcript_path = None

    # Try to get captions if available
    try:
        caption_track = yt.captions.get(language)
        if caption_track:
            caption_track.download(title=f"{output_video}.srt", output_path="videos")
            transcript = f"Transcription of video titled `{yt.title}` at {url}:\n"
            for event in caption_track.json_captions["events"]:
                if "segs" in event:
                    for seg in event["segs"]:
                        transcript += seg.get("utf8", "")
            text = (
                transcript.replace("\xa0", " ").replace("  ", " ").replace(" \n", " ")
            )
            transcript_path = os.path.abspath(f"videos/{output_video}.txt")
            with open(transcript_path, "w") as f:
                f.write(text)
    except Exception as e:
        pass  # Captions not available or failed to download

    result = f"Downloaded video from {url}\n  Video: {video_path}"
    if transcript_path:
        result += f"\n  Transcript: {transcript_path}"
    else:
        result += "\n  Transcript: Not available"
    return result


def download_videos_from_channels(channels=[]):
    if not channels:
        return "No channels provided."
    filename = datetime.now().isoformat().replace(":", "-").split(".")[0] + ".txt"
    videos = []
    for channel in channels:
        videos += get_videos_from_channel(channel)
    downloaded_files = []
    with open(filename, "r") as f:
        links = f.read().splitlines()
        for video in videos:
            if video not in links:
                result = download_video(url=video)
                downloaded_files.append(result)
                with open(filename, "a") as f:
                    f.write(video + "\n")
    return (
        "Downloaded videos from channels: "
        + ", ".join(channels)
        + "\n"
        + "\n".join(downloaded_files)
    )


def download_videos_from_list(filename="videos.txt"):
    downloaded_files = []
    with open(filename, "r") as f:
        links = f.read().splitlines()
        for video in links:
            result = download_video(url=video)
            downloaded_files.append(result)
    return "Downloaded videos from list:\n" + "\n".join(downloaded_files)


def download_captions(url: str = "", language: str = "en-US"):
    if not url:
        return "No URL provided."
    os.makedirs("captions", exist_ok=True)
    yt = YouTube(url)
    output_video = yt.title.replace(" ", "_")
    output_video = "".join([c for c in output_video if c.isalnum() or c in "._- "])

    caption_track = yt.captions.get(language)
    if not caption_track:
        return f"No captions available for language '{language}' in video: {yt.title}"

    caption_track.download(title=f"{output_video}.srt", output_path="captions")
    transcript = f"Captions of video titled `{yt.title}` at {url}:\n"
    for event in caption_track.json_captions["events"]:
        if "segs" in event:
            for seg in event["segs"]:
                transcript += seg.get("utf8", "")
    text = transcript.replace("\xa0", " ").replace("  ", " ").replace(" \n", " ")
    # Find anything between [Ad Start] and [Ad End] and remove it
    text = re.sub(r"\[Ad Start\].*?\[Ad End\]", "", text, flags=re.DOTALL)
    return text
