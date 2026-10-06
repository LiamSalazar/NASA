import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    root: Path = Path(__file__).resolve().parents[2]
    chat_model: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-5.6-luna")
    embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    api_key: str | None = os.getenv("OPENAI_API_KEY")
    include_media: bool = os.getenv("INCLUDE_MEDIA", "false").lower() == "true"
    max_single_download_mb: int = int(os.getenv("MAX_SINGLE_DOWNLOAD_MB", "50"))
    ingestion_retry_limit: int = int(os.getenv("INGESTION_RETRY_LIMIT", "3"))
    llm_extraction_enabled: bool = os.getenv("LLM_EXTRACTION_ENABLED", "false").lower() == "true"
    nvidia_api_key: str | None = os.getenv("NVIDIA_API_KEY")
    nvidia_base_url: str | None = os.getenv("NVIDIA_BASE_URL")
    nvidia_extraction_model: str | None = os.getenv("NVIDIA_EXTRACTION_MODEL")
    nvidia_phase3_model: str = os.getenv(
        "NVIDIA_PHASE3_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b"
    )
    nvidia_embedding_model: str = os.getenv("NVIDIA_EMBEDDING_MODEL", "nvidia/nemotron-3-embed-1b")
    embedding_preprocessing_version: str = "phase2-v1"
    # Optional advisory routing only. It never grants semantic classifiers any
    # authority to publish claims, alter DIRECT matching, or mutate the KG.
    semantic_classifier_backend: str = os.getenv("SEMANTIC_CLASSIFIER_BACKEND", "rule")

    @property
    def registry_path(self) -> Path:
        return self.root / "data/index/evidence.sqlite"

    @property
    def raw_manifest_path(self) -> Path:
        return self.root / "data/raw/manifest.json"
