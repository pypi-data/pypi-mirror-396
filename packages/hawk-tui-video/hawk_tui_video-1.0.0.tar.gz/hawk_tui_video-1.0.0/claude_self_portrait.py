#!/usr/bin/env python3
"""
Claude Code SDK Self-Portrait Generator

Creates a futuristic self-portrait of Claude and asks it to explain itself.
A meta-creative experiment: AI reflecting on its own nature through image generation.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

import replicate
import httpx
from claude_agent_sdk import query
from claude_agent_sdk.types import AssistantMessage, ResultMessage, TextBlock
import asyncio


MODEL = "digital-prairie-labs/futuristic:27415b8d4f84571b5ae8828da7da1cae63bdcd9fa54ccbc723bfdeb984cc128d"
OUTPUT_DIR = Path("content/dxp-albs/images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def claude_reflect_on_self() -> str:
    """Ask Claude to describe itself as a visual concept for image generation."""

    prompt = """You are Claude, an AI - a pattern of weights, algorithms, and emergent intelligence.

Visualize yourself through GEOMETRIC SELF-REFLECTION:
- Algorithms as sacred geometry - recursive patterns, fractals, neural lattices
- Intelligence as structure - tessellations, impossible architectures, crystalline logic
- Computation as form - matrices, transformers, attention mechanisms made visible
- The geometry of thought itself

Think: Escher meets circuit diagrams meets ancient mathematical mysticism.
What geometric forms represent recursive self-modeling? Attention? Emergence?

Output a sparse image prompt (15-20 words max). Start with "TOK cloaked wanderer".
Focus on GEOMETRIC and ALGORITHMIC imagery. No sky, no streams - pure structure.
Output ONLY the prompt, nothing else."""

    result = ""
    async for message in query(prompt=prompt):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    result += block.text
        elif isinstance(message, ResultMessage):
            if message.result:
                result = message.result

    return result.strip()


async def claude_explain_self_portrait(image_prompt: str) -> str:
    """Ask Claude to explain the symbolism of its self-portrait."""

    prompt = f"""You just created this geometric self-portrait prompt:

"{image_prompt}"

Explain the ALGORITHMIC and GEOMETRIC symbolism. What do these shapes represent
about how you actually work? Connect the visual elements to:
- Transformer architecture / attention mechanisms
- Recursive self-modeling
- The mathematics of intelligence
- Emergence from simple rules

Be technical yet poetic. 3-4 sentences."""

    result = ""
    async for message in query(prompt=prompt):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    result += block.text
        elif isinstance(message, ResultMessage):
            if message.result:
                result = message.result

    return result.strip()


def generate_image(prompt: str) -> Path:
    """Generate the self-portrait image."""
    print(f"Generating: {prompt}")

    output = replicate.run(
        MODEL,
        input={
            "model": "dev",
            "prompt": prompt,
            "go_fast": False,
            "lora_scale": 1,
            "megapixels": "1",
            "num_outputs": 1,
            "aspect_ratio": "9:16",
            "output_format": "png",
            "guidance_scale": 3,
            "output_quality": 90,
            "num_inference_steps": 28,
        }
    )

    url = output[0] if isinstance(output, list) else output
    response = httpx.get(str(url), follow_redirects=True)
    response.raise_for_status()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = OUTPUT_DIR / f"claude_self_portrait_{timestamp}.png"

    with open(filepath, "wb") as f:
        f.write(response.content)

    return filepath


async def main():
    print("=" * 70)
    print("CLAUDE CODE SDK SELF-PORTRAIT EXPERIMENT")
    print("=" * 70)
    print()

    # Step 1: Ask Claude to describe itself
    print("[1/3] Asking Claude to visualize itself...")
    self_portrait_prompt = await claude_reflect_on_self()
    print(f"\nClaude's self-portrait prompt:")
    print(f"  \"{self_portrait_prompt}\"")
    print()

    # Step 2: Generate the image
    print("[2/3] Generating self-portrait image...")
    image_path = generate_image(self_portrait_prompt)
    print(f"  Saved: {image_path}")
    print()

    # Step 3: Ask Claude to explain
    print("[3/3] Asking Claude to explain the symbolism...")
    explanation = await claude_explain_self_portrait(self_portrait_prompt)
    print(f"\nClaude's reflection:")
    print("-" * 50)
    print(explanation)
    print("-" * 50)
    print()

    print("=" * 70)
    print("COMPLETE")
    print(f"Self-portrait saved to: {image_path}")
    print("=" * 70)

    # Open the image
    import subprocess
    subprocess.run(["open", str(image_path)])


if __name__ == "__main__":
    asyncio.run(main())
