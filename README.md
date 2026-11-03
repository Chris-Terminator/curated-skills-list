# Curated Skills List

A collection of useful AI agent skills for development, design, automation, and content creation.

This repository brings together skills I've found worth keeping and reusing across projects. Some are taken from existing open-source projects, while others have been modified or customized to various workflows.

The goal is simple: keep a small, practical collection of skills that help AI coding agents produce better results.

## Skills

| Skill | Description |
|---|---|
| [cua-driver](./cua-driver/) | Automates native desktop applications on Windows, macOS, and Linux using accessibility trees, screenshots, and GUI controls. |
| [fal-ai-videogen](./fal-ai-videogen/) | Generates videos from images using fal.ai and Kling V3 Pro, with control over motion, duration, and aspect ratio. |
| [fix-my-ui](./fix-my-ui/) | Cleans up AI-generated interfaces, improving layouts, typography, colors, and visual consistency while giving the design more character. |
| [frontend-design](./frontend-design/) | Guides agents toward distinctive, intentional frontend designs instead of generic AI-generated layouts. |
| [playwriter](./playwriter/) | Automates an existing Chrome browser session using Playwright, including authenticated and JavaScript-heavy websites. |
| [remotion-best-practices](./remotion-best-practices/) | Provides best practices for creating programmatic videos with React and Remotion, including animation, audio, captions, and composition. |
| [seo-aeo-best-practices](./seo-aeo-best-practices/) | Covers traditional SEO and AI answer engine optimization, including metadata, structured data, technical SEO, and content quality. |
| [unslop](./unslop/) | Removes common AI writing patterns, unnecessary filler, and unnatural phrasing while preserving the intended meaning and tone. |

## Installation

Clone the repository:

```bash
git clone https://github.com/Chris-Terminator/curated-skills-list.git
```

Copy the skill folders you want into your AI agent's supported skills directory, such as `~/.agents/skills/`.

Each skill contains a `SKILL.md` file with instructions for the agent. Some skills also include supporting scripts, reference material, or additional dependencies.

Check the individual skill instructions for setup requirements.

## Notes & attribution

### fix-my-ui

[fix-my-ui](./fix-my-ui/) is a lightly rewritten version of [heydamir/unslop](https://github.com/heydamir/unslop).

I renamed it to `fix-my-ui` to avoid a naming conflict with the separate `unslop` skill from [pstack](https://github.com/cursor/plugins/tree/main/pstack/skills/unslop), which focuses on cleaning up AI-generated writing.

The two skills serve different purposes:

- **fix-my-ui:** Improves the visual quality of AI-generated interfaces.
- **unslop:** Improves the quality and naturalness of AI-generated writing.

### Playwriter

[Playwriter](https://playwriter.dev/) is a browser automation tool that lets AI agents control your existing Chrome or Chromium-based browser using Playwright. Unlike tools that launch a separate browser, it works with your current sessions, cookies, and extensions through a Chrome extension and CLI.

The included skill provides instructions for using Playwriter effectively with AI agents.

### Upstream skill credits

The following skills come from existing open-source projects. Credit goes to their original creators and maintainers.

| Skill | Original project |
|---|---|
| [cua-driver](./cua-driver/) | [Cua AI — trycua/cua](https://www.skills.sh/trycua/cua/cua-driver) |
| [frontend-design](./frontend-design/) | [Anthropic — anthropics/skills](https://www.skills.sh/anthropics/skills/frontend-design) |
| [remotion-best-practices](./remotion-best-practices/) | [Remotion — remotion-dev/skills](https://www.skills.sh/remotion-dev/skills/remotion-best-practices) |
| [seo-aeo-best-practices](./seo-aeo-best-practices/) | [Sanity — sanity-io/agent-toolkit](https://www.skills.sh/sanity-io/agent-toolkit/seo-aeo-best-practices) |
| [unslop](./unslop/) | [pstack — cursor/plugins](https://github.com/cursor/plugins/tree/main/pstack/skills/unslop) ([skills.sh](https://www.skills.sh/cursor/plugins/unslop)) |

This is a curated collection, not a claim of original authorship over the included third-party skills. Refer to the upstream projects for their documentation, licensing, and updates.

---

*Collected and maintained for sharing. The list will evolve as I find useful skills or refine existing ones.*
