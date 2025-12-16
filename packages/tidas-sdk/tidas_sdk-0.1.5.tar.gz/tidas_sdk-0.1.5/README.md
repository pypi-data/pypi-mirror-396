# TIDAS Python SDK

[中文文档](README-zh.md)

Type-safe Python SDK for working with ILCD/TIDAS life-cycle assessment (LCA) data.
It provides generated Pydantic models plus higher-level helpers so you can read,
manipulate, validate and export ILCD-compatible datasets from Python.

## Installation

### From PyPI

```bash
pip install tidas-sdk
```

### From source (this repository)

```bash
cd sdks/python
uv sync --group dev
```

## Quick Start

Run the end-to-end sample to see the core features in action:

```bash
uv run python examples/usage.py
```

Minimal usage example:

```python
from tidas_sdk import create_process

process = create_process({})
process.process_data_set.process_information.data_set_information.name.base_name.set_text(
    "Sample Process", lang="en"
)

print(process.to_json())
```

## Basic Usage

### Creating entities

```python
from tidas_sdk import create_process, create_flow, create_source

process = create_process({})
flow = create_flow({})
source = create_source({})
```

You can also build entities directly from ILCD‑style JSON:

```python
from pathlib import Path
from tidas_sdk import create_process_from_json

process = create_process_from_json(Path("process.json"))
```

Or start from ILCD XML when you already have the canonical `.xml` datasets:

```python
from pathlib import Path
from tidas_sdk import create_process_from_xml, TidasProcess

process = create_process_from_xml(Path("process.xml"))
# or, if you prefer to work with the class directly
process = TidasProcess.from_xml(Path("process.xml"))
```

### Working with multilingual fields

```python
name_list = process.process_data_set.process_information.data_set_information.name.base_name
name_list.set_text("Sample Process", lang="en")
name_list.set_text("示例工艺", lang="zh")
print(name_list.get_text("en"))
```

### Validation and export

```python
is_valid = process.validate()          # Pydantic (and optional JSON Schema) validation
json_payload = process.to_json()       # ILCD‑compatible dict
xml_payload = process.to_xml()         # ILCD XML string
```

## Main Features

- JSON ➜ Object: `create_process()` and other factory helpers build rich entity objects from complete or partial ILCD JSON.
- Object ➜ JSON: `to_json()` returns ILCD-compatible dictionaries suitable for storage or downstream tooling.
- Multilingual fields: `MultiLangList` with `set_text()` / `get_text()` simplifies `@xml:lang` / `#text` handling.
- Strong typing: generated Pydantic models expose full type hints for IDE autocompletion and static checking.
- On-demand validation: `validate()` runs Pydantic and optional JSON Schema validation when your dataset is ready.
- XML export: `to_xml()` converts entities into ILCD XML for interoperability with other LCA systems.

See `examples/usage.py` for a step‑by‑step walkthrough of these features.

## Development Workflow (for contributors)

```bash
# Install / update dependencies
uv sync --group dev

# Linting & formatting
uv run ruff check src
uv run ruff format src

# Type checking
uv run mypy src

# Tests
uv run pytest
```

## Project Layout

- `src/tidas_sdk`: Core implementation and generated models
- `examples/usage.py`: Feature walkthrough used in this README
- `scripts/`: Utility scripts for code generation and maintenance

For questions or contributions, open an issue or pull request at https://github.com/tiangong-lca/tidas-sdk.
