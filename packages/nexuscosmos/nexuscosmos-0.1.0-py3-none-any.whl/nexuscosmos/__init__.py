"""NexusCosmos - Reusable library for astronomical data acquisition and analysis

A generic, dataset-agnostic framework for fetching and parsing astronomical 
observations from any data source. Includes built-in caching, rate-limiting, 
and configuration management.

Architecture:
- Generic base classes (BaseAcquisitionClient, BaseParser) for implementing new datasets
- Dataset-specific implementations in datasets/ subpackage (Horizons, MPC, GAIA, etc.)
- Reusable utilities (caching, rate-limiting) work with any astronomical data source
- Flexible data models (EphemerisData, OrbitalElements) support custom fields

Quick Start:
    from nexuscosmos import HorizonsClient, HorizonsQueryConfig
    
    client = HorizonsClient()
    config = HorizonsQueryConfig.quick_ephemeris(object_id='1I')
    result = client.fetch_data(config)
"""

__version__ = "0.1.0"

# Core data models (generic, dataset-agnostic)
from .models import EphemerisData, OrbitalElements

# Generic base classes for implementing new datasets
from .acquisition_base import BaseAcquisitionClient, BaseParser, GenericAcquisitionClient, AsyncGenericAcquisitionClient
from .parsers_base import BaseTextParser, BaseCSVParser, BaseJSONParser, CompositeParser

# Dataset-specific implementations (Horizons)
from .datasets.horizons import HorizonsClient, HorizonsParser

# Utilities (reusable for any dataset)
from .utils import RateLimiter, ExponentialBackoff
from .cache import FileCache
from .export import DataExporter

# Configuration management
from .config import QueryConfig, CacheConfig, ClientConfig, PRESETS

__all__ = [
    # Core data models
    "EphemerisData",
    "OrbitalElements",
    
    # Generic base classes (for implementing new datasets)
    "BaseAcquisitionClient",
    "BaseParser",
    "GenericAcquisitionClient",
    "AsyncGenericAcquisitionClient",
    "BaseTextParser",
    "BaseCSVParser",
    "BaseJSONParser",
    "CompositeParser",
    
    # Horizons-specific implementation
    "HorizonsClient",
    "HorizonsParser",
    
    # Utilities
    "RateLimiter",
    "ExponentialBackoff",
    "FileCache",
    "DataExporter",
    
    # Configuration
    "QueryConfig",
    "CacheConfig",
    "ClientConfig",
    "PRESETS",
]
