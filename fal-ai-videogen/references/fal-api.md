# fal.ai Kling V3 Pro API Reference

## Overview

- **Endpoint**: `https://queue.fal.run/fal-ai/kling-video/v3/pro/image-to-video`
- **Model ID**: `fal-ai/kling-video/v3/pro/image-to-video`
- **Category**: image-to-video

## Pricing

For every second of video generated, the charge is **$0.112** (audio off) or **$0.168** (audio on). If voice control is used while generating audio, the charge is **$0.196**. For example, a 5s video with audio on and voice control will cost **$0.98**.

## Input Schema

The API accepts these parameters as JSON:

- **`start_image_url`** (`string`, *required*): URL of the image or base64 data URI to be used for the video.
- **`end_image_url`** (`string`, *optional*): URL of the image or base64 data URI to be used for the end of the video.
- **`prompt`** (`string`, *optional*): Text prompt for video generation detailing motion/action.
- **`duration`** (`string`, *optional*): The duration in seconds. Default: `"5"`. Options: `"3"`, `"4"`, `"5"`, `"6"`, `"7"`, `"8"`, `"9"`, `"10"`, `"11"`, `"12"`, `"13"`, `"14"`, `"15"`. Note: this skill defaults to `"6"`.
- **`aspect_ratio`** (`string`, *optional*): The aspect ratio of the output video. Options: `"16:9"`, `"9:16"`, `"1:1"`.
- **`generate_audio`** (`boolean`, *optional*): Whether to generate native audio. Default: `true` (but this skill defaults to `false`).
- **`negative_prompt`** (`string`, *optional*): Default: `"blur, distort, and low quality"`.
- **`cfg_scale`** (`float`, *optional*): CFG scale default: `0.5`. Range: `0` to `1`.

*Note: the exact duration parameter expects a string integer, e.g. `"6"`.*

## Output Schema

The API returns:

```json
{
  "video": {
    "file_name": "out.mp4",
    "file_size": 8431922,
    "content_type": "video/mp4",
    "url": "https://v3b.fal.media/.../out.mp4"
  }
}
```

## Queue API Workflow

The model is asynchronous.

1. **Submit**: POST to `https://queue.fal.run/fal-ai/kling-video/v3/pro/image-to-video` with `Authorization: Key $FAL_KEY`. Returns a `request_id`, `status_url`, and `response_url`.
2. **Poll Status**: GET the `status_url`. Response status will be `"IN_QUEUE"`, `"IN_PROGRESS"`, or `"COMPLETED"`.
3. **Get Result**: GET the `response_url` once status is `"COMPLETED"`.
