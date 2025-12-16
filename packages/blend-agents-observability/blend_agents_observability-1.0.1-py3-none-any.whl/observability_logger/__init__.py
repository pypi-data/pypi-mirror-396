"""
Observability Logger for Strands Agents.

This package provides instrumentation for capturing execution graphs
of multi-step AI agent workflows.

Usage:
    from observability_logger import AgentLogger

    logger = AgentLogger(trace_id="trace_123")
    node = logger.miscellaneous("node_1", {"name": "Validation"}, "content")
    logger.end()
"""

import logging

from .models.agent_logger import AgentLogger, Edge
from .models.node import (
    Node,
    MiscellaneousNode,
    ParallelNode,
    RouterNode,
    AgentNode
)
from .config.settings import ObservabilityConfig, get_config, reset_config
from .core.utils import generate_id, get_current_timestamp_ms

# Version
__version__ = "0.1.0"

# Public API
__all__ = [
    'AgentLogger',
    'Edge',
    'Node',
    'MiscellaneousNode',
    'ParallelNode',
    'RouterNode',
    'AgentNode',
    'ObservabilityConfig',
    'get_config',
    'reset_config',
    'generate_id',
    'get_current_timestamp_ms'
]

# Configure package-level logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
