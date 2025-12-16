#!/usr/bin/env python3
"""FastAPI server for ytextract - Download YouTube videos via HTTP API."""
import glob
import os
import signal
import sys
from typing import List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn

import ytextract
from ytextract import YouTube
from ytextract.innertube import _default_clients

app = FastAPI(
    title="ytextract API",
    description="HTTP API for downloading YouTube videos and captions",
    version=ytextract.__version__,
)


# Pydantic models for request/response
class VideoRequest(BaseModel):
    url: str
    language: str = "en-US"


class CaptionsRequest(BaseModel):
    url: str
    language: str = "en-US"


class FileRequest(BaseModel):
    filename: str


class ChannelsRequest(BaseModel):
    channels: List[str]


class DownloadResponse(BaseModel):
    status: str
    message: str
    result: Optional[str] = None


# PID file for server management
PID_FILE = os.path.expanduser("~/.ytextract_server.pid")
VIDEOS_DIR = os.path.abspath("videos")


def find_video_by_id(video_id: str) -> Optional[str]:
    """Find an existing video file by video ID or partial match."""
    os.makedirs(VIDEOS_DIR, exist_ok=True)

    # Search for any mp4 file that might match
    for filepath in glob.glob(os.path.join(VIDEOS_DIR, "*.mp4")):
        filename = os.path.basename(filepath)
        # Check if video_id is in the filename
        if video_id in filename:
            return filepath
    return None


def get_video_title_from_id(video_id: str) -> str:
    """Get the video title from YouTube to match against local files."""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        yt = YouTube(url)
        title = yt.title.replace(" ", "_")
        title = "".join([c for c in title if c.isalnum() or c in "._- "])
        return title
    except:
        try:
            _default_clients["ANDROID_EMBED"] = _default_clients["MWEB"]
            url = f"https://www.youtube.com/watch?v={video_id}"
            yt = YouTube(url)
            title = yt.title.replace(" ", "_")
            title = "".join([c for c in title if c.isalnum() or c in "._- "])
            return title
        except:
            return None


def download_video_by_id(video_id: str, language: str = "en-US") -> str:
    """Download a video by its ID and return the file path."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    ytextract.download_video(url=url, language=language)

    # Find the downloaded file
    title = get_video_title_from_id(video_id)
    if title:
        video_path = os.path.join(VIDEOS_DIR, f"{title}.mp4")
        if os.path.exists(video_path):
            return video_path

    # Fallback: search for any matching file
    return find_video_by_id(video_id)


def write_pid():
    """Write the current process PID to file."""
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))


def read_pid() -> Optional[int]:
    """Read the server PID from file."""
    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return None
    return None


def remove_pid():
    """Remove the PID file."""
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)


@app.on_event("startup")
async def startup_event():
    """Write PID file on startup."""
    write_pid()


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up PID file on shutdown."""
    remove_pid()


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "ytextract API",
        "version": ytextract.__version__,
        "endpoints": {
            "GET /": "This help message",
            "GET /health": "Health check",
            "GET /watch?v={video_id}&language={lang}": "Stream a video (downloads if not cached)",
            "POST /download/video": "Download a video by URL (body: {url, language?})",
            "POST /download/captions": "Download captions only (body: {url, language?})",
            "POST /download/file": "Download videos from a file",
            "POST /download/channels": "Download videos from channels",
        },
        "defaults": {"language": "en-US"},
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": ytextract.__version__}


@app.get("/watch")
async def watch_video(
    v: str = Query(..., description="YouTube video ID"),
    language: str = Query(
        "en-US", description="Language code for captions (e.g., en-US)"
    ),
):
    """
    Stream a YouTube video. Downloads if not already cached locally.

    Usage: /watch?v=VIDEO_ID&language=en-US
    """
    if not v:
        raise HTTPException(status_code=400, detail="Missing video ID parameter 'v'")

    # Clean the video ID (remove any extra parameters)
    video_id = v.split("&")[0].strip()

    # First, check if we already have this video
    video_path = find_video_by_id(video_id)

    if not video_path:
        # Try to match by title
        title = get_video_title_from_id(video_id)
        if title:
            potential_path = os.path.join(VIDEOS_DIR, f"{title}.mp4")
            if os.path.exists(potential_path):
                video_path = potential_path

    # If still not found, download it
    if not video_path or not os.path.exists(video_path):
        try:
            video_path = download_video_by_id(video_id, language=language)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to download video: {str(e)}"
            )

    if not video_path or not os.path.exists(video_path):
        raise HTTPException(
            status_code=404, detail="Video not found and could not be downloaded"
        )

    # Stream the video file
    def iterfile():
        with open(video_path, "rb") as f:
            while chunk := f.read(1024 * 1024):  # 1MB chunks
                yield chunk

    file_size = os.path.getsize(video_path)
    filename = os.path.basename(video_path)

    return StreamingResponse(
        iterfile(),
        media_type="video/mp4",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
            "Content-Length": str(file_size),
            "Accept-Ranges": "bytes",
        },
    )


@app.post("/download/video", response_model=DownloadResponse)
async def download_video(request: VideoRequest):
    """Download a YouTube video with optional language for captions."""
    if "youtu" not in request.url:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    try:
        result = ytextract.download_video(url=request.url, language=request.language)
        return DownloadResponse(
            status="success",
            message=f"Downloaded video from {request.url}",
            result=str(result),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/download/captions", response_model=DownloadResponse)
async def download_captions(request: CaptionsRequest):
    """Download captions for a YouTube video in specified language."""
    if "youtu" not in request.url:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    try:
        result = ytextract.download_captions(url=request.url, language=request.language)
        return DownloadResponse(
            status="success",
            message=f"Downloaded captions from {request.url}",
            result=str(result),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/download/file", response_model=DownloadResponse)
async def download_from_file(request: FileRequest):
    """Download videos from a text file (one URL per line)."""
    if not os.path.exists(request.filename):
        raise HTTPException(
            status_code=404, detail=f"File not found: {request.filename}"
        )

    try:
        result = ytextract.download_videos_from_list(filename=request.filename)
        return DownloadResponse(
            status="success",
            message=f"Downloaded videos from file: {request.filename}",
            result=str(result),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/download/channels", response_model=DownloadResponse)
async def download_from_channels(request: ChannelsRequest):
    """Download videos from YouTube channels."""
    if not request.channels:
        raise HTTPException(status_code=400, detail="No channels provided")

    try:
        result = ytextract.download_videos_from_channels(channels=request.channels)
        return DownloadResponse(
            status="success",
            message=f"Downloaded videos from channels: {', '.join(request.channels)}",
            result=str(result),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def start_server(host: str = "0.0.0.0", port: int = 8765, daemon: bool = False):
    """Start the ytextract server."""
    if daemon:
        # Fork to run in background
        pid = os.fork()
        if pid > 0:
            # Parent process
            print(f"ytextract server started in background (PID: {pid})")
            print(f"Server running at http://{host}:{port}")
            sys.exit(0)
        else:
            # Child process - detach from terminal
            os.setsid()
            # Redirect stdout/stderr to /dev/null
            sys.stdout = open(os.devnull, "w")
            sys.stderr = open(os.devnull, "w")

    print(f"Starting ytextract server at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")


def stop_server():
    """Stop the running ytextract server."""
    pid = read_pid()
    if pid is None:
        print("No ytextract server is running (PID file not found)")
        return False

    try:
        os.kill(pid, signal.SIGTERM)
        remove_pid()
        print(f"ytextract server stopped (PID: {pid})")
        return True
    except ProcessLookupError:
        remove_pid()
        print(f"Server process {pid} not found (stale PID file removed)")
        return False
    except PermissionError:
        print(f"Permission denied to stop server (PID: {pid})")
        return False


def server_status() -> dict:
    """Check if the server is running."""
    pid = read_pid()
    if pid is None:
        return {"running": False, "message": "No server running"}

    try:
        os.kill(pid, 0)  # Check if process exists
        return {"running": True, "pid": pid, "message": f"Server running (PID: {pid})"}
    except ProcessLookupError:
        remove_pid()
        return {
            "running": False,
            "message": "Server not running (stale PID file removed)",
        }
    except PermissionError:
        return {"running": True, "pid": pid, "message": f"Server running (PID: {pid})"}


if __name__ == "__main__":
    start_server()
