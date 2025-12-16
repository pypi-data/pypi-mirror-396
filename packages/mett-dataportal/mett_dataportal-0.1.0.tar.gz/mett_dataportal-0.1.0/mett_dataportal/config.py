"""Configuration helpers for the METT Data Portal client and CLI."""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Any, Dict

from .constants import DEFAULT_BASE_URL
from .exceptions import ConfigurationError
from .version import __version__

try:  # Python 3.11+
    import tomllib as tomli  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    import tomli  # type: ignore[no-redef]


DEFAULT_TIMEOUT = 30
CONFIG_PATH = Path.home() / ".mett" / "config.toml"


@dataclass(slots=True)
class Config:
    """Runtime configuration for the DataPortal client."""

    base_url: str = DEFAULT_BASE_URL
    jwt_token: str | None = None
    timeout: int = DEFAULT_TIMEOUT
    verify_ssl: bool = True
    user_agent: str = field(default_factory=lambda: f"mett-dataportal-client/{__version__}")

    @property
    def authorization_header(self) -> str | None:
        token = self.jwt_token
        return f"Bearer {token}" if token else None


def _load_from_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with path.open("rb") as fh:
            return tomli.load(fh)
    except (OSError, tomli.TOMLDecodeError) as exc:  # type: ignore[attr-defined]
        raise ConfigurationError(f"Unable to read config file {path}: {exc}") from exc


def _coerce_bool(value: Any | None) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    raise ConfigurationError(f"Cannot coerce value '{value}' to bool")


def get_config(*, config_path: Path | None = None, env: Dict[str, str] | None = None) -> Config:
    """Load configuration from environment variables and optional TOML file."""

    env = env or os.environ
    path = config_path or CONFIG_PATH

    file_data = _load_from_file(path)
    cfg = Config()

    cfg.base_url = env.get("METT_BASE_URL") or file_data.get("base_url", cfg.base_url)
    cfg.jwt_token = env.get("METT_JWT") or file_data.get("jwt_token")

    timeout_val = env.get("METT_TIMEOUT") or file_data.get("timeout")
    if timeout_val:
        try:
            cfg.timeout = int(timeout_val)
        except (TypeError, ValueError) as exc:  # pragma: no cover
            raise ConfigurationError("METT_TIMEOUT must be an integer") from exc

    verify_val = env.get("METT_VERIFY_SSL") or file_data.get("verify_ssl")
    coerced = _coerce_bool(verify_val)
    if coerced is not None:
        cfg.verify_ssl = coerced

    cfg.user_agent = env.get("METT_USER_AGENT") or file_data.get("user_agent", cfg.user_agent)

    return cfg


__all__ = ["Config", "get_config", "CONFIG_PATH"]
