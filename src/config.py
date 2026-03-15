from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import yaml
from dotenv import load_dotenv


@dataclass
class PipelineConfig:
    llm_enabled: bool = False
    llm_provider: str = "groq"
    llm_model: str = "llama-3.3-70b-versatile"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    llm_timeout_seconds: int = 60
    similarity_threshold: float = 0.84
    high_temp_threshold_c: float = 45.0
    medium_temp_threshold_c: float = 35.0
    output_format: str = "markdown"


DEFAULT_CONFIG = PipelineConfig()


def load_config(config_path: str | None) -> PipelineConfig:
    load_dotenv()

    if not config_path:
        return _env_override(DEFAULT_CONFIG)

    path = Path(config_path)
    if not path.exists():
        return _env_override(DEFAULT_CONFIG)

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    cfg = PipelineConfig(
        llm_enabled=bool(data.get("llm_enabled", DEFAULT_CONFIG.llm_enabled)),
        llm_provider=str(data.get("llm_provider", DEFAULT_CONFIG.llm_provider)),
        llm_model=str(data.get("llm_model", DEFAULT_CONFIG.llm_model)),
        groq_base_url=str(data.get("groq_base_url", DEFAULT_CONFIG.groq_base_url)),
        llm_timeout_seconds=int(data.get("llm_timeout_seconds", DEFAULT_CONFIG.llm_timeout_seconds)),
        similarity_threshold=float(data.get("similarity_threshold", DEFAULT_CONFIG.similarity_threshold)),
        high_temp_threshold_c=float(data.get("high_temp_threshold_c", DEFAULT_CONFIG.high_temp_threshold_c)),
        medium_temp_threshold_c=float(data.get("medium_temp_threshold_c", DEFAULT_CONFIG.medium_temp_threshold_c)),
        output_format=str(data.get("output_format", DEFAULT_CONFIG.output_format)),
    )
    return _env_override(cfg)


def _env_override(cfg: PipelineConfig) -> PipelineConfig:
    llm_model = os.getenv("LLM_MODEL", cfg.llm_model)
    llm_provider = os.getenv("LLM_PROVIDER", cfg.llm_provider)
    groq_base_url = os.getenv("GROQ_BASE_URL", cfg.groq_base_url)
    llm_enabled_env = os.getenv("LLM_ENABLED")
    llm_enabled = cfg.llm_enabled if llm_enabled_env is None else llm_enabled_env.lower() == "true"
    llm_timeout_env = os.getenv("LLM_TIMEOUT_SECONDS")
    llm_timeout_seconds = cfg.llm_timeout_seconds if llm_timeout_env is None else int(llm_timeout_env)
    return PipelineConfig(
        llm_enabled=llm_enabled,
        llm_provider=llm_provider,
        llm_model=llm_model,
        groq_base_url=groq_base_url,
        llm_timeout_seconds=llm_timeout_seconds,
        similarity_threshold=cfg.similarity_threshold,
        high_temp_threshold_c=cfg.high_temp_threshold_c,
        medium_temp_threshold_c=cfg.medium_temp_threshold_c,
        output_format=cfg.output_format,
    )
