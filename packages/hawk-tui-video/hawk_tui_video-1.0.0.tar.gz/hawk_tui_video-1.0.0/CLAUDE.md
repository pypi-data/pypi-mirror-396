# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hawk TUI is a terminal-based TikTok video creator. It generates images using custom Replicate models and assembles them into 9:16 videos with FFmpeg.

## Build & Run Commands

```bash
# Install dependencies
pip install -e .
# or with uv
uv pip install -e .

# Run the TUI
python -m hawk.main
# or after install
hawk
```

## Architecture

The app uses Textual for the TUI framework. Main flow: `main.py` → `HawkTUI` app (in `app.py`) → pushes `SplashScreen` on mount → user interaction with three-panel layout.

**Core modules:**
- `app.py` - Main `HawkTUI` Textual app with three-panel layout (ProjectSelector, ImageList, MenuPanel) and keybindings
- `config.py` - `Project` dataclass and `PROJECTS` dict mapping slugs to Replicate models; color palette; API keys from `.env`
- `replicate_client.py` - Wraps Replicate API: `generate_image()`, `get_project_images()`, `delete_image()`
- `video.py` - FFmpeg wrapper: `create_slideshow()` builds TikTok-format videos (1080x1920)
- `screens/splash.py` - ASCII art splash screen shown on startup

**Data flow:**
1. User selects project (1/2/3) → updates `current_project` reactive
2. User enters prompt (g) → `replicate_client.generate_image()` → saves to `content/{project}/images/`
3. User selects images (Tab/a) → `create_video` action → `video.create_slideshow()` → saves to `content/{project}/exports/`

## Projects & Models

| Slug | Model | Trigger |
|------|-------|---------|
| wedding-vision | digital-prairie-labs/spring-wedding | TOK |
| latin-bible | digital-prairie-labs/catholic-prayers-v2.1 | (none) |
| dxp-labs | digital-prairie-labs/futuristic | TOK |

## Keyboard Shortcuts

- `1/2/3` - Switch project
- `g` - Generate images (opens prompt input)
- `Tab/Space` - Toggle image selection
- `a` - Select all images
- `Esc` - Clear selection
- `v` - Create video from selected
- `o/Enter` - Open current image in Preview.app
- `b` - Browse project folder in Finder
- `d` - Delete selected images
- `↑/↓` or `j/k` - Navigate image list
- `q` - Quit

## Environment Variables

Required in `.env`:
- `REPLICATE_API_TOKEN` - Replicate API
- `ANTHROPIC_API_KEY` - Claude API (optional)

## Git Workflow

Commit after each batch of changes with descriptive messages.
