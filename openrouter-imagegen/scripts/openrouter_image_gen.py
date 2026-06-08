#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request


API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemini-3.1-flash-image-preview"
DEFAULT_IMAGE_SIZE = "1K"
DEFAULT_ASPECT_RATIO = "1:1"
FALLBACK_OUT_DIR = "output/openrouter-imagegen"
CODEBASE_ASSET_DIRS = (
    "public/images/generated",
    "public/generated",
    "src/assets/generated",
    "assets/generated",
)

ALLOWED_MODELS = {
    "google/gemini-3.1-flash-image-preview",
    "google/gemini-3-pro-image-preview",
}

STANDARD_ASPECT_RATIOS = {
    "1:1",
    "2:3",
    "3:2",
    "3:4",
    "4:3",
    "4:5",
    "5:4",
    "9:16",
    "16:9",
    "21:9",
}

FLASH_ONLY_ASPECT_RATIOS = {
    "1:4",
    "4:1",
    "1:8",
    "8:1",
}

ALLOWED_IMAGE_SIZES = {"1K", "2K", "4K"}


def die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def read_prompt(prompt: str | None, prompt_file: str | None) -> str:
    if prompt and prompt_file:
        die("Use --prompt or --prompt-file, not both.")
    if prompt_file:
        path = Path(prompt_file)
        if not path.exists():
            die(f"Prompt file not found: {path}")
        value = path.read_text(encoding="utf-8").strip()
    else:
        value = (prompt or "").strip()
    if not value:
        die("Missing prompt. Use --prompt or --prompt-file.")
    return value


def ensure_api_key(dry_run: bool) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if api_key:
        return api_key
    if dry_run:
        return ""
    die("OPENROUTER_API_KEY is not set.")
    return ""


def validate_model(model: str) -> None:
    if model not in ALLOWED_MODELS:
        die("model must be one of: " + ", ".join(sorted(ALLOWED_MODELS)))


def validate_image_size(image_size: str) -> None:
    if image_size not in ALLOWED_IMAGE_SIZES:
        die("image-size must be one of: 1K, 2K, 4K.")


def validate_aspect_ratio(model: str, aspect_ratio: str) -> None:
    if aspect_ratio in STANDARD_ASPECT_RATIOS:
        return
    if aspect_ratio in FLASH_ONLY_ASPECT_RATIOS and model == "google/gemini-3.1-flash-image-preview":
        return
    allowed = sorted(STANDARD_ASPECT_RATIOS)
    if model == "google/gemini-3.1-flash-image-preview":
        allowed += sorted(FLASH_ONLY_ASPECT_RATIOS)
    die("aspect-ratio is not allowed for the selected model: " + ", ".join(allowed))


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


def build_user_content(prompt: str, image_paths: list[str], image_urls: list[str]) -> str | list[dict]:
    if not image_paths and not image_urls:
        return prompt

    content: list[dict] = [{"type": "text", "text": prompt}]

    for image_url in image_urls:
        content.append({"type": "image_url", "image_url": {"url": image_url}})

    for image_path in image_paths:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": image_file_to_data_url(image_path)},
            }
        )

    return content


def build_messages(prompt: str, system_prompt: str | None, image_paths: list[str], image_urls: list[str]) -> list[dict]:
    messages: list[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append(
        {
            "role": "user",
            "content": build_user_content(prompt, image_paths, image_urls),
        }
    )
    return messages


def build_modalities(model: str) -> list[str]:
    if model.startswith("google/"):
        return ["image", "text"]
    return ["image"]


def build_payload(args: argparse.Namespace, prompt: str) -> dict:
    payload = {
        "model": args.model,
        "messages": build_messages(prompt, args.system, args.image, args.image_url),
        "modalities": build_modalities(args.model),
        "image_config": {
            "aspect_ratio": args.aspect_ratio,
            "image_size": args.image_size,
        },
    }
    if args.max_tokens is not None:
        payload["max_tokens"] = args.max_tokens
    return payload


def post_json(api_key: str, payload: dict) -> dict:
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
            error_obj = parsed.get("error")
            if isinstance(error_obj, dict):
                message = error_obj.get("message") or body
            else:
                message = parsed.get("message") or body
        except json.JSONDecodeError:
            message = body
        die(f"OpenRouter request failed ({exc.code}): {message}")
    except urllib.error.URLError as exc:
        die(f"Network error: {exc}")
    return {}


def extract_images(response_json: dict) -> list[str]:
    choices = response_json.get("choices") or []
    if not choices:
        die("No choices returned by OpenRouter.")

    message = choices[0].get("message") or {}
    images = message.get("images") or []
    output: list[str] = []

    for image in images:
        image_url = image.get("image_url") or image.get("imageUrl") or {}
        url = image_url.get("url")
        if isinstance(url, str) and url.startswith("data:image/"):
            output.append(url)

    if output:
        return output

    text = message.get("content")
    if text:
        die(f"No generated images found in response. Assistant content: {text}")
    die("No generated images found in response.")
    return []


def parse_data_url(data_url: str) -> tuple[str, bytes]:
    prefix, encoded = data_url.split(",", 1)
    mime_type = prefix.split(";")[0].removeprefix("data:")
    return mime_type, base64.b64decode(encoded)


def extension_for_mime_type(mime_type: str) -> str:
    return {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }.get(mime_type, ".bin")


def resolve_default_out_dir() -> str:
    cwd = Path.cwd()
    for candidate in CODEBASE_ASSET_DIRS:
        candidate_path = cwd / candidate
        parent = candidate_path.parent
        if candidate_path.exists() or parent.exists():
            return candidate
    return FALLBACK_OUT_DIR


def output_paths(out_dir: Path, stem: str, image_count: int, mime_types: list[str]) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for index in range(image_count):
        suffix = "" if image_count == 1 else f"-{index + 1}"
        ext = extension_for_mime_type(mime_types[index])
        paths.append(out_dir / f"{stem}{suffix}{ext}")
    return paths


def write_outputs(images: list[str], out_dir: str, stem: str, force: bool) -> list[Path]:
    mime_types: list[str] = []
    payloads: list[bytes] = []

    for image in images:
        mime_type, image_bytes = parse_data_url(image)
        mime_types.append(mime_type)
        payloads.append(image_bytes)

    paths = output_paths(Path(out_dir), stem, len(payloads), mime_types)

    for path, image_bytes in zip(paths, payloads):
        if path.exists() and not force:
            die(f"Output already exists: {path}. Use --force to overwrite.")
        path.write_bytes(image_bytes)
        print(f"Wrote {path}")

    return paths


def write_raw_response(response_json: dict, out_dir: str, stem: str, force: bool) -> Path:
    path = Path(out_dir) / f"{stem}.json"
    if path.exists() and not force:
        die(f"Raw response file already exists: {path}. Use --force to overwrite.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(response_json, indent=2), encoding="utf-8")
    print(f"Wrote {path}")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate or edit images through OpenRouter.")
    parser.add_argument("--prompt")
    parser.add_argument("--prompt-file")
    parser.add_argument("--system")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--image", action="append", default=[])
    parser.add_argument("--image-url", action="append", default=[])
    parser.add_argument("--image-size", "--resolution", dest="image_size", default=DEFAULT_IMAGE_SIZE)
    parser.add_argument("--aspect-ratio", default=DEFAULT_ASPECT_RATIO)
    parser.add_argument("--max-tokens", type=int)
    parser.add_argument("--out-dir", default=resolve_default_out_dir())
    parser.add_argument("--stem", default="image")
    parser.add_argument("--save-json", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    prompt = read_prompt(args.prompt, args.prompt_file)
    validate_model(args.model)
    validate_image_size(args.image_size)
    validate_aspect_ratio(args.model, args.aspect_ratio)
    api_key = ensure_api_key(args.dry_run)

    payload = build_payload(args, prompt)

    if args.dry_run:
        print(json.dumps(payload, indent=2))
        return 0

    response_json = post_json(api_key, payload)
    images = extract_images(response_json)
    write_outputs(images, args.out_dir, args.stem, args.force)
    if args.save_json:
        write_raw_response(response_json, args.out_dir, args.stem, args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())