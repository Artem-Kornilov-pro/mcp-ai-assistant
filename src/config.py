"""Application configuration loaded from environment."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class LLMConfig:
    api_key: str
    folder_id: str
    model: str
    temperature: float = 0.3
    max_tokens: int = 2000
    timeout: float = 30.0


@dataclass
class Config:
    llm: LLMConfig
    github_token: str
    google_service_account_path: Path
    workspace_dir: Path


def load_config(env_path: str | None = None) -> Config:
    """Load configuration from .env file and environment variables."""

    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()

    llm = LLMConfig(
        api_key=_require("YANDEX_CLOUD_API_KEY"),
        folder_id=_require("YANDEX_CLOUD_FOLDER_ID"),
        model=os.getenv("YANDEX_CLOUD_MODEL", "deepseek-v4-flash/latest"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000")),
        timeout=float(os.getenv("LLM_TIMEOUT", "30.0")),
    )

    return Config(
        llm=llm,
        github_token=os.getenv("GITHUB_TOKEN", ""),
        google_service_account_path=Path(
            os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", "./credentials/service-account.json")
        ),
        workspace_dir=Path(os.getenv("WORKSPACE_DIR", "./workspace")),
    )


def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Environment variable {key} is required but not set")
    return value
