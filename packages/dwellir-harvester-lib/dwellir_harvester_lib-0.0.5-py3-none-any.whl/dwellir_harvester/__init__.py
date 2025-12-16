"""Collectors for gathering node metadata.

This package provides base classes for creating collectors and specific collector
implementations for different blockchain clients and system information.
"""
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("dwellir-harvester-lib")
except PackageNotFoundError:
    __version__ = "0.0.0"

# Base classes
from .collector_base import (
    BlockchainCollector,
    GenericCollector,
    CollectorError,
)

# Re-export collectors so the framework can discover them by import.
from .collectors.null import NullCollector
from .collectors.dummychain import DummychainCollector
from .collectors.host import HostCollector
from .collectors.juju import JujuCollector
# from .collectors.substrate import SubstrateCollector

# What this package exports
__all__ = [
    # Base classes
    "BlockchainCollector",
    "GenericCollector",
    "CollectorError",
    "__version__",

    # Concrete collectors
    "NullCollector",
    "DummychainCollector",
#    "PolkadotCollector",
    "HostCollector",
    "JujuCollector"
]
