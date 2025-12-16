"""
DEPRECATED: Use nexuscosmos.datasets.horizons instead.

Legacy Horizons API client kept for backward compatibility.
"""
import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import time

from .utils import RateLimiter
from .parsers import HorizonsParser

logger = logging.getLogger(__name__)


class HorizonsClient:
    """DEPRECATED: Use nexuscosmos.datasets.horizons.HorizonsClient instead."""

    INTERSTELLAR_OBJECTS = {
        "1I/Oumuamua": "A/2017 U1",
        "2I/Borisov": "C/2019 Q4",
        "3I/ATLAS": "C/2025 N1"
    }

    def __init__(
        self,
        base_url: str = "https://ssd.jpl.nasa.gov/api/horizons.api",
        timeout: int = 30,
        request_delay: float = 1.0,
        rate_limiter: Optional[RateLimiter] = None
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.request_delay = request_delay
        self.rate_limiter = rate_limiter or RateLimiter(max_attempts=10, window_minutes=1)
        self.last_request_time = 0.0

    def _rate_limit(self):
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()

    def _resolve_designation(self, object_id: str) -> str:
        return self.INTERSTELLAR_OBJECTS.get(object_id, object_id)

    def get_observer_ephemeris(
        self,
        object_id: str,
        start_time: str,
        stop_time: str,
        step_size: str = "1d",
        observer: str = "@399"
    ) -> Dict[str, Any]:
        """Fetch observer-based ephemeris (RA, DEC, distances, magnitude)."""
        designation = self._resolve_designation(object_id)
        self._rate_limit()

        params = {
            'format': 'text',
            'COMMAND': f"'{designation}'",
            'OBJ_DATA': 'YES',
            'MAKE_EPHEM': 'YES',
            'EPHEM_TYPE': 'OBSERVER',
            'CENTER': f"'{observer}'",
            'START_TIME': f"'{start_time}'",
            'STOP_TIME': f"'{stop_time}'",
            'STEP_SIZE': f"'{step_size}'",
            'QUANTITIES': "'1,9,20,23,24'",
            'CSV_FORMAT': 'YES',
            'CAL_FORMAT': 'BOTH',
            'ANG_FORMAT': 'DEG'
        }

        try:
            logger.info(f"Fetching observer ephemeris for {designation}")
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            from .parsers import HorizonsParser
            data = HorizonsParser.parse_observer_ephemeris(response.text)

            return {
                'success': True,
                'object': designation,
                'data': data,
                'raw_data': response.text,
                'timestamp': datetime.utcnow().isoformat()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return {'success': False, 'object': designation, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error: {e}")
            return {'success': False, 'object': designation, 'error': str(e)}

    def get_state_vectors(
        self,
        object_id: str,
        start_time: str,
        stop_time: str,
        step_size: str = "1d",
        center: str = "@sun"
    ) -> Dict[str, Any]:
        """Fetch heliocentric state vectors (position and velocity)."""
        designation = self._resolve_designation(object_id)
        self._rate_limit()

        params = {
            'format': 'text',
            'COMMAND': f"'{designation}'",
            'OBJ_DATA': 'YES',
            'MAKE_EPHEM': 'YES',
            'EPHEM_TYPE': 'VECTORS',
            'CENTER': f"'{center}'",
            'START_TIME': f"'{start_time}'",
            'STOP_TIME': f"'{stop_time}'",
            'STEP_SIZE': f"'{step_size}'",
            'REF_PLANE': 'ECLIPTIC',
            'VEC_TABLE': '3',
            'CSV_FORMAT': 'YES',
            'OUT_UNITS': 'AU-D',
            'VEC_CORR': 'NONE'
        }

        try:
            logger.info(f"Fetching state vectors for {designation}")
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = HorizonsParser.parse_state_vectors(response.text)

            return {
                'success': True,
                'object': designation,
                'data': data,
                'raw_data': response.text,
                'timestamp': datetime.utcnow().isoformat()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return {'success': False, 'object': designation, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error: {e}")
            return {'success': False, 'object': designation, 'error': str(e)}

    def get_orbital_elements(self, object_id: str) -> Dict[str, Any]:
        """Fetch orbital elements for comparison."""
        designation = self._resolve_designation(object_id)
        self._rate_limit()

        params = {
            'format': 'text',
            'COMMAND': f"'{designation}'",
            'OBJ_DATA': 'YES',
            'MAKE_EPHEM': 'NO'
        }

        try:
            logger.info(f"Fetching orbital elements for {designation}")
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            elements = HorizonsParser.parse_orbital_elements(response.text)

            return {
                'success': True,
                'object': designation,
                'elements': elements,
                'raw_data': response.text,
                'timestamp': datetime.utcnow().isoformat()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return {'success': False, 'object': designation, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error: {e}")
            return {'success': False, 'object': designation, 'error': str(e)}

    def fetch_live_position(self, object_id: str, observer: str = "@399") -> Dict[str, Any]:
        """Fetch current position of object (live mode)."""
        now = datetime.utcnow()
        start_time = now.strftime("%Y-%m-%d %H:%M")
        stop_time = (now + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        return self.get_observer_ephemeris(
            object_id, start_time, stop_time, step_size="1h", observer=observer
        )

    def fetch_query_mode(
        self,
        object_id: str,
        start_time: str,
        stop_time: str,
        step_size: str = "1d",
        observer: str = "@399"
    ) -> Dict[str, Any]:
        """Fetch custom time range data (query mode)."""
        return self.get_observer_ephemeris(object_id, start_time, stop_time, step_size, observer)
