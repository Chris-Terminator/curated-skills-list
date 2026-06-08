---
name: fal-ai-videogen
description: Use this skill when generating videos from still images using fal.ai's Kling V3 Pro model. Features include image-to-video generation, motion prompts, video duration control (3-15 seconds), aspect ratio selection, and a CLI workflow that requires the `FAL_KEY` environment variable.
---

# fal-ai-videogen Skill

This skill lets you generate high-quality video from a starting image using fal.ai's Kling V3 Pro API (`fal-ai/kling-video/v3/pro/image-to-video`).

## When to use

- You need to animate a static image into a video.
- You need to generate a video based on an image and a motion prompt.
- The user requests a video of a specific duration (up to 15s) from an image.

## Supported Model

- **Kling V3 Pro**: `fal-ai/kling-video/v3/pro/image-to-video` via the fal.ai Queue API. 

## Pricing Note

Using this skill costs money against the user's fal.ai account. The current rate is **$0.112 per second** of generated video (without audio). A standard 6s video costs ~$0.67.

## Required Environment

You must have the `FAL_KEY` environment variable set.
- If it is not set, instruct the user to configure it.
- **NEVER** log or expose the `FAL_KEY` value.

## Usage Rules

- **Image Requirement:** You must provide a start image path (`--image`) or a URL (`--image-url`).
- **End Image:** An optional end image can be provided via (`--end-image`) or (`--end-image-url`).
- **Aspect Ratio:** Defaults to `16:9`. The `--aspect-ratio` flag only allows `16:9` or `9:16`. (The API also technically supports 1:1, but restrict to 16:9 and 9:16 per the prompt constraints).
- **Duration:** Defaults to `6` seconds. Allowed range is 3 to 15 seconds.
- **Audio:** Defaults to `false` (no audio). Do not add audio unless explicitly instructed to.
- **Async Execution:** Generation takes time for videos. Run the script using the standard `bash` tool.

## Command Examples

The skill script is located at: `~/.verdent/skills/fal-ai-videogen/scripts/fal_video_gen.py`

### Basic execution with local image
```bash
python ~/.verdent/skills/fal-ai-videogen/scripts/fal_video_gen.py --image "input/scene.jpg" --prompt "The camera slowly pans out"
```

### Basic execution with remote image
```bash
python ~/.verdent/skills/fal-ai-videogen/scripts/fal_video_gen.py --image-url "https://example.com/character.png" --prompt "The character blinks and smiles"
```

### Specifying configuration
```bash
python ~/.verdent/skills/fal-ai-videogen/scripts/fal_video_gen.py \
  --image "input/portrait.jpg" \
  --prompt "Hair blowing in the wind" \
  --duration "8" \
  --aspect-ratio "9:16" \
  --stem "portrait-video"
```

### Dry Run (Testing options before generating)
```bash
python ~/.verdent/skills/fal-ai-videogen/scripts/fal_video_gen.py --image-url "https://example.com/img.jpg" --dry-run
```