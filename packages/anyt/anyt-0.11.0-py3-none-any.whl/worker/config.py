"""Worker configuration management."""

import os
from pathlib import Path
from typing import Any, Optional, cast

import yaml
from pydantic import BaseModel, Field, field_validator


class AIConfig(BaseModel):
    """AI/LLM configuration."""

    provider: str = "anthropic"
    model: str = "claude-haiku-4-5-20251001"
    max_tokens: int = 4096
    temperature: float = 0.7
    api_key: str


class ExecutionConfig(BaseModel):
    """Task execution configuration."""

    timeout: int = 600
    auto_retry: bool = True
    max_retries: int = 3
    retry_delay: int = 60


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "INFO"
    file: str
    console: bool = True
    format: str = "pretty"


class WorkerConfig(BaseModel):
    """Worker configuration."""

    agent_id: str
    api_key: str
    workspace_id: int
    poll_interval: int = 30
    max_concurrent_tasks: int = 1
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    ai: AIConfig
    logging: LoggingConfig

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format."""
        if not v.startswith("anyt_agent_"):
            raise ValueError("API key must start with 'anyt_agent_'")
        return v

    @property
    def config_path(self) -> Path:
        """Path to config file."""
        return Path.cwd() / ".anyt" / "workers" / f"{self.agent_id}.yaml"

    @classmethod
    def load(cls, agent_id: str) -> "WorkerConfig":
        """Load worker config from file."""
        config_path = Path.cwd() / ".anyt" / "workers" / f"{agent_id}.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Worker config not found: {config_path}")

        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Substitute environment variables
        data = cls._substitute_env_vars(data)

        return cls(**data)

    @classmethod
    def load_from_file(cls, config_file: Path) -> "WorkerConfig":
        """Load worker config from custom file."""
        with open(config_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        data = cls._substitute_env_vars(data)
        return cls(**data)

    @classmethod
    def create_default(
        cls, agent_id: str, api_key: str, workspace_id: Optional[int] = None
    ) -> "WorkerConfig":
        """Create default worker config."""
        # Auto-detect workspace_id if not provided
        # (load from .anyt/anyt.json)
        if workspace_id is None:
            from cli.config import WorkspaceConfig

            ws_config = WorkspaceConfig.load()
            if ws_config is None:
                raise ValueError(
                    "No workspace config found. Please initialize workspace first or provide workspace_id."
                )
            workspace_id = int(ws_config.workspace_id)

        config = cls(
            agent_id=agent_id,
            api_key=api_key,
            workspace_id=workspace_id,
            ai=AIConfig(
                provider="anthropic",
                model="claude-haiku-4-5-20251001",
                api_key="${ANTHROPIC_API_KEY}",
            ),
            logging=LoggingConfig(file=f".anyt/logs/worker-{agent_id}.log"),
        )
        return config

    def save(self) -> None:
        """Save worker config to file."""
        config_path = self.config_path
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)

    @staticmethod
    def _substitute_env_vars(data: Any) -> Any:
        """Recursively substitute environment variables."""
        if isinstance(data, dict):
            data_dict: dict[Any, Any] = cast(dict[Any, Any], data)  # type: ignore[redundant-cast]
            return {
                k: WorkerConfig._substitute_env_vars(v) for k, v in data_dict.items()
            }
        elif isinstance(data, list):
            data_list: list[Any] = cast(list[Any], data)  # type: ignore[redundant-cast]
            return [WorkerConfig._substitute_env_vars(item) for item in data_list]
        elif isinstance(data, str) and data.startswith("${") and data.endswith("}"):
            env_var = data[2:-1]
            value = os.getenv(env_var)
            if value is None:
                raise ValueError(f"Environment variable not set: {env_var}")
            return value
        return data
