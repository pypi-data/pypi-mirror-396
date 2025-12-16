"""
JPL Horizons-specific data acquisition and parsing.

Provides HorizonsClient for fetching data from NASA JPL's Horizons API
and HorizonsParser for parsing Horizons-format responses.

Example:
    from nexuscosmos.datasets.horizons import HorizonsClient
    client = HorizonsClient(enforce_rate_limit=True)
    ephemeris = client.get_observer_ephemeris(
        object_id='1I',
        start_time='2025-01-01',
        stop_time='2025-01-10',
        observer='500@-5'  # JPL, Pasadena
    )
"""

from .client import HorizonsClient
from .parser import HorizonsParser

__all__ = ["HorizonsClient", "HorizonsParser"]
