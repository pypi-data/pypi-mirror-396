# Dwellir Harvester Lib

Core SDK for building and running Dwellir harvesters. It provides the collector base classes, loader helpers, RPC utilities, and the shared blockchain metadata schema used by `dwellir-harvester`.

## Features
- Collector base classes (`CollectorBase`, `GenericCollector`, `BlockchainCollector`) with result/metadata helpers
- Collector loader with plugin paths and entry point support
- Schema validation helpers and bundled `blockchain_node_metadata.schema.json`
- Simple runner to execute a collector class directly (`python -m dwellir_harvester.lib.run`)
- RPC helpers for JSON-RPC, Substrate, and EVM-compatible nodes

## Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage
```python
from dwellir_harvester.core import collect_all, bundled_schema_path

result = collect_all([
    "host",  # or your plugin collector name
], schema_path=bundled_schema_path())
print(result)
```

Run a collector class directly (module:Class):
```bash
# Built-in null collector
python -m dwellir_harvester.lib.run dwellir_harvester.collectors.null:NullCollector

# From the dwellir_harvester package
python -m dwellir_harvester.lib.run examples.plugins.sample_collector:SamplePluginCollector

```

## Packaging notes
- Python 3.9+
- Entry point group for collectors: `dwellir_harvester.collectors`
- Bundled schema is included as package data under `dwellir_harvester/data/`

## Building (offline-friendly)
Use the sibling checkout pattern:
1. Make sure you have a venv with build tools (and system site packages to avoid missing setuptools):
   ```bash
   python3 -m venv --system-site-packages .venv
   source .venv/bin/activate
   pip install --upgrade pip build
   ```
2. Build the library without isolation (reuses your env, no downloads):
   ```bash
   python -m build --no-isolation
   ```
Artifacts land in `dist/` (`.whl` and `.tar.gz`). If you depend on this from the app as a sibling path, the existing `file:../dwellir-harvester-lib` PEP 508 spec in the app works; for publishing, set a versioned requirement there instead.


## Publish (Python package)

```bash
# build
python3 -m pip install build twine
python3 -m build  # creates dist/*.tar.gz and dist/*.whl

# upload to TestPyPI first (recommended)
python3 -m twine upload -r testpypi dist/*

# Install from testpypi
python3 -m venv .venv
source .venv/bin/activate
# Pull in deps from real, this is needed only on testpypi 
pip3 install jsonschema>=4.25.1 psutil>=7.1.3 requests>=2.32.5
# Install from testpypi
pip3 install --index-url https://test.pypi.org/simple/ --no-deps dwellir-harvester-lib

# then to PyPI
python3 -m twine upload dist/*