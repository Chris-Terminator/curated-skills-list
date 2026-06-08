# CLI Usage

Run the bundled script:

```bash
python scripts/openrouter_image_gen.py --prompt "Your prompt here"
```

## Required environment variable

```bash
OPENROUTER_API_KEY=...
```

Use a local environment variable. Do not paste the key into chat.

## Core flags

- `--prompt` inline prompt text
- `--prompt-file` prompt from a text file
- `--model` one of:
  - `google/gemini-3.1-flash-image-preview`
  - `google/gemini-3-pro-image-preview`
- `--image-size` or `--resolution` one of `1K`, `2K`, `4K`
- `--aspect-ratio` one of the documented ratios
- `--image` attach a local image file, repeatable
- `--image-url` attach a remote image URL, repeatable
- `--system` optional system instruction
- `--out-dir` output directory
- `--stem` base filename stem
- `--save-json` save the raw API response
- `--dry-run` print request JSON without sending it
- `--force` overwrite existing files

## Examples

### Fast default generation

```bash
python scripts/openrouter_image_gen.py --prompt "Editorial product photo of a matte black skincare bottle on brushed steel"
```

### 4K wide hero image

```bash
python scripts/openrouter_image_gen.py --prompt "Premium landing page hero image for an AI automation agency, dark cinematic gradients, restrained composition" --model "google/gemini-3-pro-image-preview" --image-size 4K --aspect-ratio 16:9 --stem hero
```

### Text plus local image attachment

```bash
python scripts/openrouter_image_gen.py --prompt "Keep the object identity, re-stage this as a luxury catalog shot with soft side lighting" --image "input/product.png" --model "google/gemini-3.1-flash-image-preview" --image-size 2K --aspect-ratio 4:5 --stem catalog
```

### Text plus multiple remote images

```bash
python scripts/openrouter_image_gen.py --prompt "Combine these references into one clean architectural rendering with premium materials" --image-url "https://example.com/ref-1.jpg" --image-url "https://example.com/ref-2.jpg" --model "google/gemini-3-pro-image-preview" --image-size 1K --aspect-ratio 3:2 --stem composite
```

### Dry run

```bash
python scripts/openrouter_image_gen.py --prompt "Minimal poster with brutalist typography" --model "google/gemini-3.1-flash-image-preview" --image-size 1K --aspect-ratio 4:1 --dry-run
```

## Aspect ratios

Standard ratios:

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

Flash-only extended ratios:

- `1:4`
- `4:1`
- `1:8`
- `8:1`

## Output behavior

- Default output targets a codebase-friendly asset folder when one exists:
  - `public/images/generated`
  - `public/generated`
  - `src/assets/generated`
  - `assets/generated`
- If none of those paths are available, the script falls back to `output/openrouter-imagegen`.
- Generated images are decoded from OpenRouter data URLs and written to files.
- Extensions are inferred from the returned MIME type.
- Single-image responses write `stem.ext`.
- Multi-image responses write `stem-1.ext`, `stem-2.ext`, and so on.