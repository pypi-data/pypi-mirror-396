# Blend Agents Observability

[![PyPI version](https://img.shields.io/pypi/v/blend-agents-observability.svg)](https://pypi.org/project/blend-agents-observability/)
[![License](https://img.shields.io/pypi/l/blend-agents-observability.svg)](https://pypi.org/project/blend-agents-observability/)
[![Build Status](https://img.shields.io/circleci/project/github/user/repo/tree/main.svg)](https://circleci.com/gh/user/repo/tree/main)

Enterprise-grade observability library for instrumenting multi-step AI agent systems. Capture, process, and visualize complex agent execution graphs with ease.

> **Note:** This package is owned by **Blend360** and is intended for **internal usage only**.

## Features

- **Manual Instrumentation**: Explicit control over trace creation and node lifecycle for precise observability.
- **AWS Kinesis Integration**: Stream observability events directly to AWS Kinesis Data Streams.
- **Type-Safe Events**: Leverages Pydantic for robust event validation, ensuring data integrity.
- **Resilient by Design**: Gracefully handles errors and fails silently, preventing observability from impacting your application's stability.
- **Detailed Agent Tracking**: Capture fine-grained details of agent execution, including reasoning steps and tool usage.
- **Parallel Workflow Support**: Built-in support for tracing parallel execution branches and sub-traces.

## Installation

```bash
pip install blend-agents-observability
```

## Quick Start

Here's a simple example of how to get started with the `AgentLogger`:

```python
from observability_logger import AgentLogger, generate_id

# 1. Initialize the logger for a new trace
logger = AgentLogger(
    trace_id=generate_id("trace_"),
    workflow_id="data_processing_v1",
    title="Data Processing Workflow"
)

# 2. Create a node to represent a step in your workflow
# This node is auto-completed upon creation.
validation_node = logger.miscellaneous(
    node_id=generate_id("node_"),
    config={"name": "Input Validation", "description": "Validate incoming data"},
    content="Validated 5 fields successfully",
    metadata={"fields_validated": 5}
)

# 3. Create another node
processing_node = logger.miscellaneous(
    node_id=generate_id("node_"),
    config={"name": "Data Transformation"},
    content="Transformed data to target schema"
)

# 4. Connect the nodes with an edge to show the flow
logger.edge(validation_node, processing_node)

# 5. End the trace when the workflow is complete
logger.end(status="completed")
```

This will generate a trace with two connected nodes and emit the corresponding events to your configured Kinesis stream.