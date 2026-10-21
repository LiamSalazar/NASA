"""Tests never reach a live provider: scientific stages stay on NVIDIA with no Anthropic key."""

import os

# Set before nasa_fire_ai.config loads .env, which never overrides a set variable.
os.environ["SCIENCE_PROVIDER"] = "nvidia"
os.environ["ANTHROPIC_API_KEY"] = ""
