"""Configuration management for tgwrap."""

# pylint: disable=too-many-instance-attributes

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class TgWrapConfig:  # pylint: disable=too-many-instance-attributes
    """Central configuration for tgwrap."""

    # Core settings
    verbose: bool = False
    debug: bool = False
    working_dir: Optional[str] = None

    # Terragrunt settings
    planfile_name: str = "planfile"
    tg_file: str = "terragrunt.hcl"
    minimum_tg_version: str = "0.88.0"

    # Security settings
    max_arg_length: int = 1000
    max_path_length: int = 255
    allowed_system_paths: List[str] = field(default_factory=list)

    # Performance settings
    parallel_execution: bool = True
    max_workers: int = 4
    timeout_seconds: int = 3600

    # Output settings
    log_level: str = "INFO"
    output_format: str = "text"

    @classmethod
    def from_env(cls) -> "TgWrapConfig":
        """Create configuration from environment variables."""
        return cls(
            verbose=os.getenv("TGWRAP_VERBOSE", "false").lower() == "true",
            debug=os.getenv("TGWRAP_DEBUG", "false").lower() == "true",
            working_dir=os.getenv("TGWRAP_WORKING_DIR"),
            planfile_name=os.getenv("TGWRAP_PLANFILE_NAME", "planfile"),
            max_workers=int(os.getenv("TGWRAP_MAX_WORKERS", "4")),
            timeout_seconds=int(os.getenv("TGWRAP_TIMEOUT", "3600")),
            log_level=os.getenv("TGWRAP_LOG_LEVEL", "INFO"),
            output_format=os.getenv("TGWRAP_OUTPUT_FORMAT", "text"),
        )

    @classmethod
    def from_file(cls, config_path: str) -> "TgWrapConfig":
        """Create configuration from a JSON config file."""
        path = Path(config_path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Config file not found: {path}")

        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)

        env_config = cls.from_env()
        for key, value in data.items():
            if hasattr(env_config, key):
                setattr(env_config, key, value)

        return env_config

    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []

        if self.max_workers < 1 or self.max_workers > 100:
            errors.append("max_workers must be between 1 and 100")

        if self.timeout_seconds < 1:
            errors.append("timeout_seconds must be positive")

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            errors.append("log_level must be one of: DEBUG, INFO, WARNING, ERROR")

        if self.output_format not in ["text", "json", "yaml"]:
            errors.append("output_format must be one of: text, json, yaml")

        return errors

    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return {
            "verbose": self.verbose,
            "debug": self.debug,
            "working_dir": self.working_dir,
            "planfile_name": self.planfile_name,
            "tg_file": self.tg_file,
            "minimum_tg_version": self.minimum_tg_version,
            "max_arg_length": self.max_arg_length,
            "max_path_length": self.max_path_length,
            "parallel_execution": self.parallel_execution,
            "max_workers": self.max_workers,
            "timeout_seconds": self.timeout_seconds,
            "log_level": self.log_level,
            "output_format": self.output_format,
        }
