"""Replicate API client for image generation."""

import os
import httpx
import replicate
from pathlib import Path
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

# Ensure token is set
if os.getenv('REPLICATE_API_TOKEN'):
    os.environ['REPLICATE_API_TOKEN'] = os.getenv('REPLICATE_API_TOKEN')

from hawk.config import Project, REPLICATE_DEFAULT_PARAMS

# Cache for model versions
_model_versions: dict[str, str] = {}


def _get_model_version(model_name: str) -> str:
    """Get the latest version for a model, caching the result."""
    if model_name not in _model_versions:
        model = replicate.models.get(model_name)
        _model_versions[model_name] = f"{model_name}:{model.latest_version.id}"
    return _model_versions[model_name]


def generate_image(
    project: Project,
    prompt: str,
    num_outputs: int = 1,
    aspect_ratio: str = "9:16",
    seed: Optional[int] = None,
) -> list[Path]:
    """
    Generate images using a project's custom Replicate model.

    Returns list of saved image paths.
    """
    project.ensure_dirs()

    # Build the prompt with trigger word if needed
    if project.trigger:
        full_prompt = f"{project.trigger} {prompt}"
    else:
        full_prompt = prompt

    # Build input params
    input_params = {
        **REPLICATE_DEFAULT_PARAMS,
        "prompt": full_prompt,
        "num_outputs": num_outputs,
        "aspect_ratio": aspect_ratio,
    }

    if seed is not None:
        input_params["seed"] = seed

    # Run the model with explicit version
    model_version = _get_model_version(project.model)
    output = replicate.run(model_version, input=input_params)

    # Download images
    saved_paths = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    urls = output if isinstance(output, list) else [output]

    for i, url in enumerate(urls):
        # Generate filename
        safe_prompt = "".join(c if c.isalnum() or c in " -_" else "" for c in prompt[:30])
        safe_prompt = safe_prompt.strip().replace(" ", "_")
        filename = f"{timestamp}_{safe_prompt}_{i+1}.png"
        filepath = project.images_dir / filename

        # Download
        response = httpx.get(str(url), follow_redirects=True)
        response.raise_for_status()

        with open(filepath, "wb") as f:
            f.write(response.content)

        saved_paths.append(filepath)

    return saved_paths


def generate_batch(
    project: Project,
    prompts: list[str],
    aspect_ratio: str = "9:16",
) -> list[Path]:
    """Generate images for multiple prompts."""
    all_paths = []
    for prompt in prompts:
        paths = generate_image(project, prompt, aspect_ratio=aspect_ratio)
        all_paths.extend(paths)
    return all_paths


def get_project_images(project: Project) -> list[Path]:
    """Get all images in a project's images folder."""
    project.ensure_dirs()
    extensions = {".png", ".jpg", ".jpeg", ".webp"}
    images = [
        f for f in project.images_dir.iterdir()
        if f.suffix.lower() in extensions
    ]
    return sorted(images, key=lambda x: x.stat().st_mtime, reverse=True)


def delete_image(image_path: Path) -> bool:
    """Delete an image file."""
    try:
        image_path.unlink()
        return True
    except Exception:
        return False
