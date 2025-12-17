"""Project and model configuration."""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / "content"


@dataclass
class Project:
    """A content project with its Replicate model."""
    name: str
    slug: str
    model: str
    trigger: str
    description: str

    @property
    def images_dir(self) -> Path:
        return CONTENT_DIR / self.slug / "images"

    @property
    def audio_dir(self) -> Path:
        return CONTENT_DIR / self.slug / "audio"

    @property
    def exports_dir(self) -> Path:
        return CONTENT_DIR / self.slug / "exports"

    def ensure_dirs(self):
        """Create project directories if they don't exist."""
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)


# Your 3 custom Replicate models
PROJECTS = {
    "wedding-vision": Project(
        name="Wedding Vision",
        slug="wedding-vision",
        model="digital-prairie-labs/spring-wedding",
        trigger="TOK",
        description="Spring wedding florals and bouquets",
    ),
    "latin-bible": Project(
        name="Latin Bible",
        slug="latin-bible",
        model="digital-prairie-labs/catholic-prayers-v2.1",
        trigger="",  # Uses prayer text directly
        description="Catholic prayers and religious imagery",
    ),
    "dxp-labs": Project(
        name="DXP Labs",
        slug="dxp-labs",
        model="digital-prairie-labs/futuristic",
        trigger="TOK",
        description="Futuristic sci-fi landscapes and spaceships",
    ),
}


# TikTok video settings
TIKTOK_WIDTH = 1080
TIKTOK_HEIGHT = 1920
TIKTOK_ASPECT = "9:16"

# Replicate settings
REPLICATE_DEFAULT_PARAMS = {
    "model": "dev",
    "go_fast": False,
    "lora_scale": 1,
    "megapixels": "1",
    "num_outputs": 1,
    "aspect_ratio": TIKTOK_ASPECT,
    "output_format": "png",
    "guidance_scale": 3,
    "output_quality": 90,
    "prompt_strength": 0.8,
    "extra_lora_scale": 1,
    "num_inference_steps": 28,
}

# API Keys (from .env)
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


# Color palette (CEO CLI style)
COLORS = {
    "bg": "#1a1d23",
    "fg": "#e0e0e0",
    "accent": "#c9a227",      # Gold for highlights
    "border": "#4a5f4a",       # Green borders
    "dim": "#6b7280",
    "success": "#22c55e",
    "error": "#ef4444",
}
