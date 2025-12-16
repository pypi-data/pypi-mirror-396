#!/usr/bin/env python3
"""A simple command line application to download YouTube videos."""
import argparse
import sys

import ytextract


def main():
    """Command line application to download YouTube videos."""
    parser = argparse.ArgumentParser(
        description="ytextract - Download YouTube videos and captions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ytextract https://youtube.com/watch?v=VIDEO_ID          Download a video
  ytextract --captions https://youtube.com/watch?v=ID     Download captions only
  ytextract --file videos.txt                             Download videos from a file
  ytextract --channels channel1 channel2                  Download from channels
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {ytextract.__version__}",
    )

    parser.add_argument(
        "url",
        nargs="?",
        help="YouTube video URL to download",
    )

    parser.add_argument(
        "-c",
        "--captions",
        action="store_true",
        help="Download captions only (no video)",
    )

    parser.add_argument(
        "-f",
        "--file",
        type=str,
        metavar="FILE",
        help="Download videos from a text file (one URL per line)",
    )

    parser.add_argument(
        "--channels",
        nargs="+",
        metavar="CHANNEL",
        help="Download videos from one or more YouTube channels",
    )

    args = parser.parse_args()

    # Check that at least one action is specified
    if not args.url and not args.file and not args.channels:
        parser.print_help()
        sys.exit(1)

    # Handle different modes
    if args.channels:
        print(f"Downloading videos from channels: {', '.join(args.channels)}")
        result = ytextract.download_videos_from_channels(channels=args.channels)
        print(result)

    elif args.file:
        print(f"Downloading videos from file: {args.file}")
        result = ytextract.download_videos_from_list(filename=args.file)
        print(result)

    elif args.url:
        if "youtu" not in args.url:
            print("Error: Invalid YouTube URL")
            sys.exit(1)

        if args.captions:
            print(f"Downloading captions for: {args.url}")
            result = ytextract.download_captions(url=args.url)
            print(result)
        else:
            print(f"Downloading video: {args.url}")
            result = ytextract.download_video(url=args.url)
            print(result)


if __name__ == "__main__":
    main()
