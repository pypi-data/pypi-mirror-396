"""Kinesis event emitter for the observability logger.

This module is responsible for sending observability events to AWS Kinesis.
It defines the `KinesisEmitter` class, which handles AWS client
initialization, event serialization, and robust error handling.

The primary design principle is to "fail silently," ensuring that observability
instrumentation does not interfere with the application's core functionality.
If an event fails to send, the error is logged, and the operation returns
`False`, but no exceptions are raised.
"""

import logging
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from ..config.settings import get_config
from ..models.events import ObservabilityEvent

logger = logging.getLogger(__name__)


class KinesisEmitter:
    """Handles the transmission of observability events to an AWS Kinesis stream.

    This class manages the lifecycle of the `boto3` Kinesis client, serializes
    events into the required format, and sends them to the configured stream.
    It is designed for internal use by the logger's components.

    Attributes:
        _config: The application's configuration settings.
        _client: The `boto3` Kinesis client instance.
    """

    def __init__(self) -> None:
        """Initializes the KinesisEmitter.

        The emitter loads its configuration from the environment and immediately
        attempts to initialize the `boto3` Kinesis client. AWS credentials are
        sourced via the standard `boto3` credential chain.
        """
        self._config = get_config()
        self._client: Optional[Any] = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initializes the `boto3` Kinesis client.

        This method attempts to create a Kinesis client using the configured
        AWS region. If initialization fails (e.g., due to missing credentials
        or permissions), the error is logged, and the client is set to `None`.
        This prevents further attempts to use the client.
        """
        try:
            self._client = boto3.client(
                "kinesis", region_name=self._config.aws_region
            )
            logger.debug(
                f"Initialized Kinesis client for region {self._config.aws_region}"
            )
        except Exception as e:
            logger.error(
                f"Failed to initialize Kinesis client: {e}. "
                "Events will not be sent."
            )
            self._client = None

    def emit(self, event: ObservabilityEvent) -> bool:
        """Emits a single observability event to the Kinesis stream.

        The event is first serialized to a JSON string. It is then encoded
        to UTF-8 bytes and sent to Kinesis using a `put_record` call. The
        `trace_id` of the event is used as the partition key to ensure that
        all events for a given trace are processed in order by the consumer.

        Args:
            event: The `ObservabilityEvent` to emit.

        Returns:
            True if the event was successfully sent, False otherwise.
        """
        if self._client is None:
            logger.warning(
                "Kinesis client not initialized. Dropping event: %s",
                event.event_type,
            )
            return False

        try:
            event_json = event.model_dump_json()

            response = self._client.put_record(
                StreamName=self._config.kinesis_stream_name,
                Data=event_json.encode("utf-8"),
                PartitionKey=event.trace_id,
            )

            logger.debug(
                "Emitted %s event for trace %s. Sequence: %s",
                event.event_type,
                event.trace_id,
                response.get("SequenceNumber", "unknown"),
            )
            return True

        except (BotoCoreError, ClientError) as e:
            logger.error(
                "AWS error emitting %s event: %s. Event dropped.",
                event.event_type,
                e,
            )
            return False
        except Exception as e:
            logger.error(
                "Unexpected error emitting %s event: %s. Event dropped.",
                event.event_type,
                e,
            )
            return False

    def emit_dict(self, event_dict: Dict[str, Any]) -> bool:
        """Emits an event from a dictionary, bypassing Pydantic validation.

        This method is primarily intended for testing purposes where sending a
        raw dictionary is more convenient than constructing a full
        `ObservabilityEvent` object.

        Args:
            event_dict: A dictionary that conforms to the
                `ObservabilityEvent` schema.

        Returns:
            True if the event was successfully created and sent, False otherwise.
        """
        try:
            event = ObservabilityEvent(**event_dict)
            return self.emit(event)
        except Exception as e:
            logger.error("Failed to create event from dict: %s", e)
            return False


# The global emitter instance is managed as a singleton.
_emitter: Optional[KinesisEmitter] = None


def get_emitter() -> KinesisEmitter:
    """Provides access to the global `KinesisEmitter` singleton instance.

    This function ensures that only one `KinesisEmitter` is created per
    process, allowing the underlying `boto3` client and its connections to be
    reused across all trace and node operations. The emitter is initialized

    lazily on its first access.

    Returns:
        The singleton `KinesisEmitter` instance.
    """
    global _emitter
    if _emitter is None:
        _emitter = KinesisEmitter()
    return _emitter


def reset_emitter() -> None:
    """Resets the global emitter instance.

    This function is used exclusively for testing to ensure that tests can
    run in isolation without sharing an emitter state.
    """
    global _emitter
    _emitter = None
