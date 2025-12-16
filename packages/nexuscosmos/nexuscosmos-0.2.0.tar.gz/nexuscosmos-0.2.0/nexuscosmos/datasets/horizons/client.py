"""
JPL Horizons-specific client for fetching ephemeris and orbital data.

This module implements dataset-specific acquisition logic for NASA JPL Horizons API.
It inherits from BaseAcquisitionClient to leverage generic caching and rate limiting.

Example:
    from nexuscosmos.datasets.horizons import HorizonsClient
    from nexuscosmos import HorizonsQueryConfig
    
    client = HorizonsClient(enforce_rate_limit=True)
    config = HorizonsQueryConfig.quick_ephemeris(object_id='1I')
    result = client.fetch_data(config)
"""

import requests
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from ...acquisition_base import BaseAcquisitionClient
from ...utils import RateLimiter, ExponentialBackoff
from ...cache import FileCache
from .parser import HorizonsParser

logger = logging.getLogger(__name__)


class HorizonsClient(BaseAcquisitionClient):
    """JPL Horizons API client inheriting from BaseAcquisitionClient.
    
    Handles all Horizons-specific logic:
    - URL construction with Horizons-specific parameters
    - Designation resolution for interstellar objects
    - Response parsing via HorizonsParser
    - Caching and rate limiting via base class
    """
    
    # Map friendly names to Horizons designations
    INTERSTELLAR_OBJECTS = {
        "1I/Oumuamua": "A/2017 U1",
        "1I": "A/2017 U1",
        "Oumuamua": "A/2017 U1",
        "2I/Borisov": "C/2019 Q4",
        "2I": "C/2019 Q4",
        "Borisov": "C/2019 Q4",
        "3I/ATLAS": "C/2025 N1",
        "3I": "C/2025 N1",
        "ATLAS": "C/2025 N1"
    }
    
    BASE_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
    RATE_LIMIT_KEY = "horizons_api"
    
    def __init__(
        self,
        base_url: str = BASE_URL,
        rate_limiter: Optional[RateLimiter] = None,
        backoff: Optional[ExponentialBackoff] = None,
        cache: Optional[FileCache] = None,
        timeout_seconds: float = 30.0,
        request_delay_seconds: float = 1.0,
        enforce_rate_limit: bool = True,
        max_requests_per_minute: int = 10,
    ):
        """Initialize Horizons client.
        
        Args:
            base_url: Horizons API endpoint
            rate_limiter: Custom RateLimiter (default: 10 req/min)
            backoff: Custom ExponentialBackoff
            cache: Custom FileCache
            timeout_seconds: HTTP request timeout
            request_delay_seconds: Delay between requests (minimum)
            enforce_rate_limit: Whether to enforce rate limiting
            max_requests_per_minute: Rate limit threshold
        """
        if rate_limiter is None and enforce_rate_limit:
            rate_limiter = RateLimiter(
                max_attempts=max_requests_per_minute,
                window_minutes=1
            )
        
        super().__init__(
            rate_limiter=rate_limiter,
            backoff=backoff,
            cache=cache,
            timeout_seconds=timeout_seconds,
        )
        
        self.base_url = base_url
        self.request_delay_seconds = request_delay_seconds
        self.last_request_time = 0.0
        self.parser = HorizonsParser()
    
    def fetch_data(self, query_config: Any) -> Dict[str, Any]:
        """Fetch data from Horizons using query configuration.
        
        Args:
            query_config: HorizonsQueryConfig instance
        
        Returns:
            Dict with keys: success, object, data, timestamp, (error or raw_data)
        """
        # Resolve designation (handle nicknames)
        designation = self._resolve_designation(query_config.object_id)
        
        # Check cache first
        cache_key = self._build_cache_key(query_config)
        cached = self.get_cached_data(cache_key)
        if cached is not None:
            logger.info(f"Cache hit for {designation}")
            return cached
        
        # Enforce rate limiting
        if not self._rate_limited_check(self.RATE_LIMIT_KEY):
            retry_after = self.rate_limiter.get_retry_after(self.RATE_LIMIT_KEY)
            logger.warning(f"Rate limited for {designation}. Retry after {retry_after:.1f}s")
            return {
                'success': False,
                'object': designation,
                'error': f'Rate limited. Retry after {retry_after:.1f}s'
            }
        
        # Apply request delay (Horizons asks for 1s between requests)
        self._apply_request_delay()
        
        # Determine ephemeris type from config
        ephem_type = query_config.ephem_type.upper()
        
        try:
            if ephem_type == "OBSERVER":
                result = self._fetch_observer_ephemeris(designation, query_config)
            elif ephem_type == "VECTORS":
                result = self._fetch_state_vectors(designation, query_config)
            elif ephem_type == "ELEMENTS":
                result = self._fetch_orbital_elements(designation, query_config)
            else:
                raise ValueError(f"Unknown ephemeris type: {ephem_type}")
            
            # Cache successful result
            if result.get('success'):
                self.cache_data(cache_key, result)
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {designation}: {e}")
            return {
                'success': False,
                'object': designation,
                'error': f'Request failed: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Error fetching {designation}: {e}")
            return {
                'success': False,
                'object': designation,
                'error': str(e)
            }
    
    def _fetch_observer_ephemeris(self, designation: str, config: Any) -> Dict[str, Any]:
        """Fetch observer-based ephemeris (RA, DEC, magnitude, distances)."""
        params = {
            'format': 'text',
            'COMMAND': f"'{designation}'",
            'OBJ_DATA': 'YES',
            'MAKE_EPHEM': 'YES',
            'EPHEM_TYPE': 'OBSERVER',
            'CENTER': f"'{config.observer}'",
            'START_TIME': f"'{config.start_time}'",
            'STOP_TIME': f"'{config.stop_time}'",
            'STEP_SIZE': f"'{config.step_size}'",
            'QUANTITIES': f"'{config.quantities}'",
            'CSV_FORMAT': 'YES',
            'CAL_FORMAT': 'BOTH',
            'ANG_FORMAT': 'DEG'
        }
        
        logger.info(f"Fetching observer ephemeris for {designation}")
        response = requests.get(
            self.base_url,
            params=params,
            timeout=self.timeout_seconds
        )
        response.raise_for_status()
        
        data = self.parser.parse_observer_ephemeris(response.text)
        
        return {
            'success': True,
            'object': designation,
            'ephem_type': 'OBSERVER',
            'data': data,
            'raw_data': response.text if not config.return_raw_data else None,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _fetch_state_vectors(self, designation: str, config: Any) -> Dict[str, Any]:
        """Fetch heliocentric state vectors (x, y, z, vx, vy, vz)."""
        params = {
            'format': 'text',
            'COMMAND': f"'{designation}'",
            'OBJ_DATA': 'YES',
            'MAKE_EPHEM': 'YES',
            'EPHEM_TYPE': 'VECTORS',
            'CENTER': f"'{config.center}'",
            'START_TIME': f"'{config.start_time}'",
            'STOP_TIME': f"'{config.stop_time}'",
            'STEP_SIZE': f"'{config.step_size}'",
            'REF_PLANE': 'ECLIPTIC',
            'VEC_TABLE': '3',
            'CSV_FORMAT': 'YES',
            'OUT_UNITS': 'AU-D',
            'VEC_CORR': 'NONE'
        }
        
        logger.info(f"Fetching state vectors for {designation}")
        response = requests.get(
            self.base_url,
            params=params,
            timeout=self.timeout_seconds
        )
        response.raise_for_status()
        
        data = self.parser.parse_state_vectors(response.text)
        
        return {
            'success': True,
            'object': designation,
            'ephem_type': 'VECTORS',
            'data': data,
            'raw_data': response.text if config.return_raw_data else None,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _fetch_orbital_elements(self, designation: str, config: Any) -> Dict[str, Any]:
        """Fetch orbital elements (a, e, i, Omega, w, M, period, H, G)."""
        params = {
            'format': 'text',
            'COMMAND': f"'{designation}'",
            'OBJ_DATA': 'YES',
            'MAKE_EPHEM': 'NO'
        }
        
        logger.info(f"Fetching orbital elements for {designation}")
        response = requests.get(
            self.base_url,
            params=params,
            timeout=self.timeout_seconds
        )
        response.raise_for_status()
        
        elements = self.parser.parse_orbital_elements(response.text)
        
        return {
            'success': True,
            'object': designation,
            'ephem_type': 'ELEMENTS',
            'data': elements,
            'raw_data': response.text if config.return_raw_data else None,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _resolve_designation(self, object_id: str) -> str:
        """Resolve friendly name to Horizons designation.
        
        Args:
            object_id: Friendly name or Horizons ID
        
        Returns:
            Official Horizons designation
        """
        return self.INTERSTELLAR_OBJECTS.get(object_id, object_id)
    
    def _apply_request_delay(self) -> None:
        """Apply minimum delay between requests."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.request_delay_seconds:
            time.sleep(self.request_delay_seconds - elapsed)
        self.last_request_time = time.time()
    
    def _rate_limited_check(self, key: str) -> bool:
        """Check if request is allowed under rate limits.
        
        Args:
            key: Rate limit key
        
        Returns:
            True if allowed; False if rate limited
        """
        if self.rate_limiter is None:
            return True
        return self.rate_limiter.is_allowed(key)
    
    def _build_cache_key(self, config: Any) -> str:
        """Build deterministic cache key from query config.
        
        Args:
            config: HorizonsQueryConfig instance
        
        Returns:
            Cache key string
        """
        parts = [
            config.object_id,
            config.start_time,
            config.stop_time,
            config.step_size,
            config.observer,
            config.center,
            config.ephem_type
        ]
        return f"horizons_{'_'.join(str(p).replace(' ', '_') for p in parts)}"
