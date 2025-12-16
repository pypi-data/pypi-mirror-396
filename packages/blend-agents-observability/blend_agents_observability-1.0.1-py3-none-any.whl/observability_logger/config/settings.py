"""
Configuration management for observability logger.

This module handles:
- AWS credentials via boto3 credential chain
- Environment variable loading with defaults
- Configuration validation
"""

import os
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ObservabilityConfig:
    """
    Configuration for the observability logger.

    This dataclass holds all configuration needed for the observability logger
    to connect to AWS services and emit events.

    Attributes:
        aws_region: AWS region for Kinesis (default: us-east-1)
        kinesis_stream_name: Name of the Kinesis stream to emit events to
        log_level: Logging level for the library (default: WARNING)
        enable_validation: Whether to enable Pydantic validation (default: True)

    Environment Variables:
        - KINESIS_STREAM_NAME: Required. Name of the Kinesis stream
        - AWS_REGION: Optional. AWS region (default: us-east-1)
        - OBSERVABILITY_LOG_LEVEL: Optional. Log level (default: WARNING)
        - OBSERVABILITY_ENABLE_VALIDATION: Optional. Enable validation (default: true)

    Example:
        >>> # Configuration is loaded automatically from environment
        >>> config = get_config()
        >>> print(config.kinesis_stream_name)
        'my-kinesis-stream'
    """

    # AWS Configuration
    aws_region: str
    kinesis_stream_name: str

    # Optional Configuration
    log_level: str = "WARNING"
    enable_validation: bool = True

    @classmethod
    def from_environment(cls) -> 'ObservabilityConfig':
        """
        Load configuration from environment variables.

        Required Environment Variables:
        - KINESIS_STREAM_NAME: Name of the Kinesis stream

        Optional Environment Variables:
        - AWS_REGION: AWS region (default: us-east-1)
        - OBSERVABILITY_LOG_LEVEL: Logging level (default: WARNING)
        - OBSERVABILITY_ENABLE_VALIDATION: Enable schema validation (default: true)

        Returns:
            ObservabilityConfig instance

        Raises:
            ValueError: If required environment variables are missing
        """
        kinesis_stream_name = os.environ.get('KINESIS_STREAM_NAME')
        if not kinesis_stream_name:
            raise ValueError(
                "KINESIS_STREAM_NAME environment variable is required. "
                "Please set it to your Kinesis stream name."
            )

        aws_region = os.environ.get('AWS_REGION', 'us-east-1')
        log_level = os.environ.get('OBSERVABILITY_LOG_LEVEL', 'WARNING')
        enable_validation = os.environ.get('OBSERVABILITY_ENABLE_VALIDATION', 'true').lower() == 'true'

        return cls(
            aws_region=aws_region,
            kinesis_stream_name=kinesis_stream_name,
            log_level=log_level,
            enable_validation=enable_validation
        )

    def validate(self) -> None:
        """
        Validate configuration values.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.kinesis_stream_name:
            raise ValueError("kinesis_stream_name cannot be empty")

        if not self.aws_region:
            raise ValueError("aws_region cannot be empty")

        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(
                f"Invalid log_level '{self.log_level}'. "
                f"Must be one of: {', '.join(valid_log_levels)}"
            )


# Global configuration instance (lazy-loaded)
_config: Optional[ObservabilityConfig] = None


def get_config() -> ObservabilityConfig:
    """
    Get the global ObservabilityConfig singleton instance.

    The configuration is loaded lazily on first access from environment
    variables and validated. Subsequent calls return the cached instance.

    Returns:
        ObservabilityConfig: The global configuration instance

    Raises:
        ValueError: If required environment variables are missing or invalid

    Note:
        This function is called internally by KinesisEmitter on initialization.
        Users typically don't need to call this directly.
    """
    global _config
    if _config is None:
        _config = ObservabilityConfig.from_environment()
        _config.validate()
    return _config


def reset_config() -> None:
    """Reset the global configuration instance (used for testing)."""
    global _config
    _config = None
