"""
Dataset-specific implementations of data acquisition and parsing.

This package contains implementations for various astronomical data sources:
- horizons: JPL Horizons API
- (future) mpc: Minor Planet Center
- (future) gaia: ESA GAIA catalog
- (future) custom: Template for adding new datasets

Each dataset module inherits from generic base classes defined in the main
nexuscosmos package, reusing cache, rate-limiting, and model infrastructure.

Example:
    # Using Horizons (current implementation)
    from nexuscosmos.datasets.horizons import HorizonsClient
    client = HorizonsClient()
    
    # Adding a new dataset in the future
    from nexuscosmos.datasets.mpc import MinorPlanetCenterClient
    mpc_client = MinorPlanetCenterClient()
"""

from .horizons import HorizonsClient, HorizonsParser

__all__ = ["HorizonsClient", "HorizonsParser"]
