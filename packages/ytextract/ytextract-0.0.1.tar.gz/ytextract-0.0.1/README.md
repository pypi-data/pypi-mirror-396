# ytextract

*ytextract* is a genuine, lightweight Python library (and command-line utility) for downloading YouTube videos.

## Description

YouTube is the most popular video-sharing platform in the world and as a hacker, you may encounter a situation where you want to script something to download videos. For this, I present to you: *ytextract*.

*ytextract* is a lightweight library written in Python. It has minimal dependencies and aims to be highly reliable.

*ytextract* also makes pipelining easy, allowing you to specify callback functions for different download events, such as ``on progress`` or ``on complete``.

Furthermore, *ytextract* includes a command-line utility, allowing you to download videos right from the terminal.

## Features

- Support for both progressive & DASH streams
- Easily register ``on_download_progress`` & ``on_download_complete`` callbacks
- Command-line interface included
- Caption track support
- Outputs caption tracks to .srt format (SubRip Subtitle)
- Ability to capture thumbnail URL
- Extensively documented source code

## Quickstart

### Installation

ytextract requires an installation of Python 3.7 or greater, as well as pip. (Pip is typically bundled with Python [installations](https://python.org/downloads).)

To install from PyPI with pip:

```bash
pip install ytextract
```

Or install from source:

```bash
pip install -e .
```

### Using the command-line interface

Use the `ytextract` command in a terminal to download videos, captions, or multiple videos from a list or channel.

#### Download a single video

To download a video at the highest progressive quality, you can use the following command:

```bash
ytextract https://youtube.com/watch?v=2lAe1cqCOXo
```

#### Download captions for a video

To download only captions for a video, use the `--captions` flag:

```bash
ytextract --captions https://youtube.com/watch?v=2lAe1cqCOXo
```

#### Download Videos from a list in a text file

To download multiple videos from a text file containing YouTube video URLs (one URL per line), use the `--file` flag:

```bash
ytextract --file videos.txt
```

#### Download Videos from a Channel, or multiple Channels

To download all videos from one or more YouTube channels, use the `--channels` flag followed by the channel usernames:

```bash
ytextract --channels officialalphablocks Numberblocks
```


### Using ytextract in a Python script

To download a video using the library in a script, simply import ytextract and call the helper functions directly.

#### Download a single video

Set the `url` parameter to the YouTube video URL you wish to download.

```python
import ytextract

ytextract.download(url="https://www.youtube.com/watch?v=VIDEO_ID")
```

#### Download captions for a video

Set the `url` parameter to the YouTube video URL you wish to download captions for.

```python
import ytextract

ytextract.download_captions(url="https://www.youtube.com/watch?v=VIDEO_ID")
```

#### Download Videos from a list from videos.txt

You can change the filename argument to any text file containing YouTube video URLs (one URL per line).

```python
import ytextract

ytextract.download_videos_from_list(filename="videos.txt")
```

#### Download Videos from a Channel, or multiple Channels

You can specify one or more channel usernames in the `channels` parameter to download all videos from those channels.

```python
import ytextract

ytextract.download_videos_from_channels(channels=["officialalphablocks", "Numberblocks"])
```

## License

This project is licensed under The Unlicense - see the [LICENSE](LICENSE) file for details.

## Contributing

Feel free to open an issue or a pull request at https://github.com/Josh-XT/ytextract
