#!/usr/bin/env python3
"""Optional NVIDIA extraction entry point. It never publishes candidates directly."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nasa_fire_ai.config import Settings

settings = Settings()
if not (
    settings.llm_extraction_enabled
    and settings.nvidia_api_key
    and settings.nvidia_base_url
    and settings.nvidia_extraction_model
):
    print(
        json.dumps(
            {
                "status": "PENDING_CONFIGURATION",
                "reason": "NVIDIA extraction configuration is incomplete; deterministic ingestion remains available.",
            }
        )
    )
else:
    print(
        json.dumps(
            {
                "status": "PENDING_IMPLEMENTATION_REVIEW",
                "reason": "No document is sent until a schema-constrained official NVIDIA model configuration is verified.",
            }
        )
    )
