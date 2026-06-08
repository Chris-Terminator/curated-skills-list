# OpenRouter API Notes For This Skill

This skill is built around the documented OpenRouter `chat/completions` image workflow.

## Confirmed request shape

OpenRouter documents image generation through:

- `POST https://openrouter.ai/api/v1/chat/completions`

For image generation, the docs specify:

- Use `modalities: ["image", "text"]` for models that output both text and images
- Use `modalities: ["image"]` for models that only output images

This skill uses:

- `["image", "text"]` for the two Google Gemini image-preview models

## Confirmed image input format

OpenRouter documents image input on `messages[].content` as multipart content blocks:

- text block first
- then one or more `image_url` blocks

Accepted image forms:

- direct URL
- base64 data URL

This skill maps:

- `--image-url` → direct `image_url.url`
- `--image` → local file encoded to `data:image/...;base64,...`

## Confirmed image configuration fields

OpenRouter documents `image_config` for some image generation models.

The relevant fields used here are:

- `image_config.aspect_ratio`
- `image_config.image_size`

Documented image sizes:

- `1K`
- `2K`
- `4K`
- `0.5K` for `google/gemini-3.1-flash-image-preview` only

This skill intentionally enforces a minimum of `1K`, so it does not expose `0.5K`.

## Confirmed aspect ratios

Documented standard ratios:

- `1:1`
- `2:3`
- `3:2`
- `3:4`
- `4:3`
- `4:5`
- `5:4`
- `9:16`
- `16:9`
- `21:9`

Documented flash-only extended ratios:

- `1:4`
- `4:1`
- `1:8`
- `8:1`

## Confirmed response shape

OpenRouter documents generated images on:

- `choices[0].message.images[]`

Each image item contains:

- `type: "image_url"`
- `image_url.url`

The documented return value is a base64 data URL such as:

- `data:image/png;base64,...`

This skill decodes that payload and writes it directly to disk.

## Model notes gathered from docs and model pages

### `google/gemini-3.1-flash-image-preview`

- Image generation and editing model
- Supports extended aspect ratios
- Supports documented `0.5K`, `1K`, `2K`, and `4K` size controls, but this skill exposes only `1K+`

### `google/gemini-3-pro-image-preview`

- Higher-end image generation and editing model
- OpenRouter model page describes stronger text rendering, multi-image blending, identity preservation, localized edits, lighting adjustments, and support for `2K/4K` outputs with flexible aspect ratios