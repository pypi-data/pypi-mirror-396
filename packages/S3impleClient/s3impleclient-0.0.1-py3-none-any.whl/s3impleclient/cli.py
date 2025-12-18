"""
Command-line interface for S3impleClient.
"""

import argparse
import json
import sys
from pathlib import Path

from .download import DownloadConfig, configure as configure_download, download
from .upload import UploadConfig, configure as configure_upload, upload


def main():
    parser = argparse.ArgumentParser(
        prog="s3c",
        description="S3impleClient - Fast parallel HTTP/S3 downloader/uploader",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Download command
    dl_parser = subparsers.add_parser(
        "download", aliases=["dl"], help="Download a file"
    )
    dl_parser.add_argument("url", help="URL to download")
    dl_parser.add_argument(
        "dest", nargs="?", help="Destination path (default: current dir)"
    )
    dl_parser.add_argument("-o", "--output", help="Output filename")
    dl_parser.add_argument(
        "-w", "--workers", type=int, default=8, help="Max parallel workers (default: 8)"
    )
    dl_parser.add_argument(
        "-c",
        "--chunk-size",
        type=int,
        default=10,
        help="Chunk size in MB (default: 10)",
    )
    dl_parser.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress progress bar"
    )
    dl_parser.add_argument(
        "-H",
        "--header",
        action="append",
        help="Additional header (format: 'Key: Value')",
    )

    # Upload command
    ul_parser = subparsers.add_parser("upload", aliases=["ul"], help="Upload a file")
    ul_parser.add_argument("file", help="File to upload")
    ul_parser.add_argument("-u", "--url", help="Upload URL (for single-part upload)")
    ul_parser.add_argument(
        "-p",
        "--part-urls",
        help="JSON file containing list of part URLs (for multipart)",
    )
    ul_parser.add_argument(
        "-s", "--chunk-size", type=int, help="Chunk size in bytes (for multipart)"
    )
    ul_parser.add_argument("--completion-url", help="Completion URL (for multipart)")
    ul_parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=8,
        help="Max parallel workers per file (default: 8)",
    )
    ul_parser.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress progress bar"
    )
    ul_parser.add_argument(
        "-H",
        "--header",
        action="append",
        help="Additional header (format: 'Key: Value')",
    )

    args = parser.parse_args()

    match args.command:
        case "download" | "dl":
            run_download(args)
        case "upload" | "ul":
            run_upload(args)
        case None:
            parser.print_help()
            sys.exit(1)
        case _:
            parser.print_help()
            sys.exit(1)


def run_download(args):
    # Parse headers
    headers: dict[str, str] = {}
    if args.header:
        for h in args.header:
            if ": " in h:
                key, value = h.split(": ", 1)
                headers[key] = value

    # Configure downloader
    config = DownloadConfig(
        max_workers=args.workers,
        chunk_size=args.chunk_size * 1024 * 1024,
    )
    configure_download(config)

    # Determine destination
    if args.output:
        dest = Path(args.output)
    elif args.dest:
        dest = Path(args.dest)
    else:
        # Extract filename from URL
        from urllib.parse import unquote, urlparse

        parsed = urlparse(args.url)
        filename = unquote(parsed.path.split("/")[-1]) or "download"
        dest = Path(filename)

    # Run download
    result = download(
        url=args.url,
        dest=dest,
        headers=headers if headers else None,
        show_progress=not args.quiet,
    )

    if result.success:
        print(f"Downloaded: {result.path} ({result.total_bytes:,} bytes)")
        sys.exit(0)
    else:
        print(f"Download failed: {result.error}", file=sys.stderr)
        sys.exit(1)


def run_upload(args):
    # Parse headers
    headers: dict[str, str] = {}
    if args.header:
        for h in args.header:
            if ": " in h:
                key, value = h.split(": ", 1)
                headers[key] = value

    # Configure uploader
    config = UploadConfig(
        max_workers_per_file=args.workers,
    )
    configure_upload(config)

    # Check file exists
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Get part URLs if provided
    part_urls: list[str] | None = None
    if args.part_urls:
        part_urls_path = Path(args.part_urls)
        if not part_urls_path.exists():
            print(f"Part URLs file not found: {part_urls_path}", file=sys.stderr)
            sys.exit(1)
        with open(part_urls_path) as f:
            part_urls = json.load(f)

    # Validate arguments
    if not args.url and not part_urls:
        print("Must provide either --url or --part-urls", file=sys.stderr)
        sys.exit(1)

    if part_urls and not args.chunk_size:
        print("Must provide --chunk-size for multipart upload", file=sys.stderr)
        sys.exit(1)

    # Run upload
    result = upload(
        file_path=file_path,
        upload_url=args.url,
        part_urls=part_urls,
        chunk_size=args.chunk_size,
        completion_url=args.completion_url,
        headers=headers if headers else None,
        show_progress=not args.quiet,
    )

    if result.success:
        print(f"Uploaded: {result.path} ({result.total_bytes:,} bytes)")
        if result.parts:
            print(f"Parts: {len(result.parts)}")
        sys.exit(0)
    else:
        print(f"Upload failed: {result.error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
