#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request


API_URL = "https://queue.fal.run/fal-ai/kling-video/v3/pro/image-to-video"
DEFAULT_DURATION = "6"
DEFAULT_ASPECT_RATIO = "16:9"
FALLBACK_OUT_DIR = "output/fal-videogen"
CODEBASE_ASSET_DIRS = (
    "public/videos/generated",
    "public/generated",
    "src/assets/generated",
    "assets/generated",
    "public/images/generated",
)

ALLOWED_DURATIONS = {str(i) for i in range(3, 16)}
ALLOWED_ASPECT_RATIOS = {"16:9", "9:16"}


def die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def read_prompt(prompt: str | None, prompt_file: str | None) -> str | None:
    if prompt and prompt_file:
        die("Use --prompt or --prompt-file, not both.")
    if prompt_file:
        path = Path(prompt_file)
        if not path.exists():
            die(f"Prompt file not found: {path}")
        return path.read_text(encoding="utf-8").strip()
    if prompt:
        return prompt.strip()
    return None


def ensure_api_key(dry_run: bool) -> str:
    api_key = os.getenv("FAL_KEY", "").strip()
    if api_key:
        return api_key
    if dry_run:
        return ""
    die("FAL_KEY is not set.")
    return ""


def validate_duration(duration: str) -> None:
    if duration not in ALLOWED_DURATIONS:
        die("duration must be between 3 and 15 seconds.")


def validate_aspect_ratio(aspect_ratio: str) -> None:
    if aspect_ratio not in ALLOWED_ASPECT_RATIOS:
        die("aspect-ratio must be one of: 16:9, 9:16.")


def detect_mime_type(path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(path.name)
    if mime_type in {"image/png", "image/jpeg", "image/webp", "image/gif"}:
        return mime_type
    die(f"Unsupported image type for {path}. Use png, jpeg, webp, or gif.")
    return ""


def image_file_to_data_url(path_str: str) -> str:
    path = Path(path_str)
    if not path.exists():
        die(f"Image file not found: {path}")
    mime_type = detect_mime_type(path)
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def build_payload(args: argparse.Namespace, prompt: str | None) -> dict:
    if args.image:
        start_image_url = image_file_to_data_url(args.image)
    elif args.image_url:
        start_image_url = args.image_url
    else:
        die("Either --image or --image-url must be provided.")

    payload = {
        "start_image_url": start_image_url,
        "duration": args.duration,
        "aspect_ratio": args.aspect_ratio,
        "generate_audio": args.audio,
        "negative_prompt": "blur, distort, and low quality",
        "cfg_scale": 0.5,
    }
    
    if args.end_image:
        payload["end_image_url"] = image_file_to_data_url(args.end_image)
    elif args.end_image_url:
        payload["end_image_url"] = args.end_image_url
        
    if prompt:
        payload["prompt"] = prompt

    return payload


def make_request(url: str, api_key: str, method: str = "GET", payload: dict | None = None) -> dict:
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json",
    }
    data = json.dumps(payload).encode("utf-8") if payload else None
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
            message = parsed.get("detail") or parsed.get("message") or body
        except json.JSONDecodeError:
            message = body
        die(f"fal API request failed ({exc.code}): {message}")
    except urllib.error.URLError as exc:
        die(f"Network error: {exc}")
    return {}


def submit_job(api_key: str, payload: dict) -> dict:
    print("Submitting job to fal.ai...")
    return make_request(API_URL, api_key, method="POST", payload=payload)


def poll_job(api_key: str, status_url: str, response_url: str) -> dict:
    print("Waiting for generation to finish...")
    while True:
        status_res = make_request(status_url, api_key)
        status = status_res.get("status")
        
        if status == "COMPLETED":
            print("\nJob completed successfully!")
            return make_request(response_url, api_key)
        elif status in ["IN_QUEUE", "IN_PROGRESS"]:
            queue_pos = status_res.get("queue_position")
            pos_info = f" (Position: {queue_pos})" if queue_pos is not None else ""
            print(f"\rStatus: {status}{pos_info}...", end="", flush=True)
            time.sleep(2)
        else:
            die(f"Unexpected status: {status_res}")


def resolve_default_out_dir() -> str:
    cwd = Path.cwd()
    for candidate in CODEBASE_ASSET_DIRS:
        candidate_path = cwd / candidate
        parent = candidate_path.parent
        if candidate_path.exists() or parent.exists():
            return candidate
    return FALLBACK_OUT_DIR


def download_file(url: str, dest_path: Path, force: bool) -> None:
    if dest_path.exists() and not force:
        die(f"Output already exists: {dest_path}. Use --force to overwrite.")
        
    print(f"Downloading from {url}...")
    try:
        with urllib.request.urlopen(url) as response, open(dest_path, "wb") as f:
            f.write(response.read())
        print(f"Wrote {dest_path}")
    except urllib.error.URLError as exc:
        die(f"Failed to download file: {exc}")


def write_raw_response(response_json: dict, out_dir: str, stem: str, force: bool) -> Path:
    path = Path(out_dir) / f"{stem}.json"
    if path.exists() and not force:
        die(f"Raw response file already exists: {path}. Use --force to overwrite.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(response_json, indent=2), encoding="utf-8")
    print(f"Wrote {path}")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate image-to-video using fal.ai Kling V3 Pro.")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--image", help="Local start image file to animate")
    group.add_argument("--image-url", help="URL of start image to animate")
    
    parser.add_argument("--end-image", help="Local end image file")
    parser.add_argument("--end-image-url", help="URL of end image")
    
    parser.add_argument("--prompt", help="Text prompt for video generation motion/action")
    parser.add_argument("--prompt-file", help="File containing text prompt")
    parser.add_argument("--duration", default=DEFAULT_DURATION, help="Video length 3-15 seconds (default: 6)")
    parser.add_argument("--aspect-ratio", default=DEFAULT_ASPECT_RATIO, help="Aspect ratio, 16:9 or 9:16 (default: 16:9)")
    parser.add_argument("--audio", action="store_true", help="Enable audio generation")
    
    parser.add_argument("--out-dir", default=resolve_default_out_dir(), help="Output directory")
    parser.add_argument("--stem", default="video", help="Output filename stem")
    parser.add_argument("--save-json", action="store_true", help="Save the raw API response")
    parser.add_argument("--dry-run", action="store_true", help="Print request JSON without sending")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    prompt = read_prompt(args.prompt, args.prompt_file)
    validate_duration(args.duration)
    validate_aspect_ratio(args.aspect_ratio)
    
    api_key = ensure_api_key(args.dry_run)

    payload = build_payload(args, prompt)

    if args.dry_run:
        # Avoid printing massive base64 strings in dry run
        if payload.get("start_image_url", "").startswith("data:image"):
            payload["start_image_url"] = "data:image/...;base64,[TRUNCATED]"
        if payload.get("end_image_url", "").startswith("data:image"):
            payload["end_image_url"] = "data:image/...;base64,[TRUNCATED]"
        print(json.dumps(payload, indent=2))
        return 0

    init_res = submit_job(api_key, payload)
    
    if "request_id" not in init_res:
        die(f"Invalid response from server: {init_res}")
        
    result_json = poll_job(api_key, init_res["status_url"], init_res["response_url"])
    
    video_data = result_json.get("video")
    if not video_data or "url" not in video_data:
        die("No video URL returned in response.")
        
    video_url = video_data["url"]
    
    out_dir_path = Path(args.out_dir)
    out_dir_path.mkdir(parents=True, exist_ok=True)
    
    dest_path = out_dir_path / f"{args.stem}.mp4"
    download_file(video_url, dest_path, args.force)
    
    if args.save_json:
        write_raw_response(result_json, args.out_dir, args.stem, args.force)
        
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
