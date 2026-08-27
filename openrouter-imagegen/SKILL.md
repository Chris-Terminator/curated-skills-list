---
name: openrouter-imagegen
description: "This skill should be used when generating or editing images through OpenRouter with specific OpenRouter image models, including `google/gemini-3.1-flash-image` and `google/gemini-3-pro-image`. This includes text-to-image, image-plus-text editing, local image attachments, image URL inputs, aspect ratio control, 1K/2K/4K image size selection, model overrides, and reusable CLI-driven image workflows that require `OPENROUTER_API_KEY`."
---

# OpenRouter Image Generation

Generate or edit images through OpenRouter using the bundled CLI at `scripts/openrouter_image_gen.py`. Prefer this skill when the user explicitly wants OpenRouter, wants one of the supported models, or needs image input plus text in the same request. Prefer saving outputs directly into codebase asset folders when possible so generated files are immediately usable by the project.

## When to use

- Generate a new image with OpenRouter
- Edit or transform an image by attaching one or more input images plus text
- Switch between the supported models without rewriting API code
- Control aspect ratio and image size while enforcing a minimum of `1K`
- Save generated images deterministically to codebase asset folders or a fallback output folder

## Supported models

Only use these model IDs unless the skill is explicitly updated:

- `google/gemini-3.1-flash-image`
- `google/gemini-3-pro-image`

Default to `google/gemini-3.1-flash-image` unless the user requests a different one.

## Workflow

1. Decide whether the request is pure generation or image-conditioned generation.
2. Collect the prompt, selected model, desired aspect ratio, and desired image size.
3. If the user supplied local images, attach them with `--image`. If the user supplied remote images, attach them with `--image-url`.
4. Run `scripts/openrouter_image_gen.py`.
5. Save outputs into a codebase asset directory when one is available. Fall back to `output/openrouter-imagegen` only when no suitable asset directory exists.
6. If the first result misses the target, change only the prompt or one generation parameter at a time and rerun.

## Rules

- Require `OPENROUTER_API_KEY` for live calls.
- Enforce a minimum image size of `1K`.
- Prefer `2K` by default unless the user asks for `1K` or `4K`.
- Prefer writing outputs into the codebase rather than an isolated temp folder.
- Put the text prompt before images in multipart message content.
- Use local image files as base64 data URLs and remote images as direct URLs.
- Do not invent unsupported models.
- Use the bundled CLI instead of writing one-off scripts unless the user explicitly asks for code changes to the skill itself.

## Command patterns

See `references/cli.md` for full examples. Common shapes:

### Generate

```bash
python scripts/openrouter_image_gen.py --prompt "Minimal black ceramic bottle on a stone pedestal" --image-size 2K --aspect-ratio 4:5
```

### Generate from text plus local images

```bash
python scripts/openrouter_image_gen.py --prompt "Keep the product shape, turn this into a premium studio campaign shot" --image "input/product.png" --image-size 2K --aspect-ratio 1:1
```

### Generate from text plus remote images

```bash
python scripts/openrouter_image_gen.py --prompt "Blend these references into one editorial hero image" --image-url "https://example.com/ref-1.jpg" --image-url "https://example.com/ref-2.jpg" --model "google/gemini-3-pro-image-preview" --image-size 4K --aspect-ratio 16:9
```

## Model guidance

- Use `google/gemini-3.1-flash-image` for the fastest default workflow and for extended aspect ratios such as `1:4`, `4:1`, `1:8`, and `8:1`.
- Use `google/gemini-3-pro-image` when the user wants stronger text rendering, more complex image reasoning, or premium multi-image composition.

## References

- `references/openrouter-api.md` for the relevant OpenRouter request and response contract
- `references/cli.md` for exact CLI usage and examples
- `scripts/openrouter_image_gen.py` for the deterministic execution path