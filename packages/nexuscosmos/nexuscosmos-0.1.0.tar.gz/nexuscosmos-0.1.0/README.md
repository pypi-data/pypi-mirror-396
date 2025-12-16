# NexusCosmos

A reusable, dataset-agnostic Python library for acquiring and analyzing astronomical observations from various data sources (JPL Horizons, Minor Planet Center, NASA GAIA, custom APIs, etc.).

## Key Features

- **Generic, Dataset-Agnostic Design**: Core utilities (caching, rate-limiting, data models) work with any astronomical data source
- **Flexible Data Models**: `EphemerisData` and `OrbitalElements` support custom fields for dataset-specific parameters
- **Built-in Utilities**: Rate limiting, exponential backoff, file-based caching with TTL
- **Extensible Architecture**: Base classes for implementing new datasets without reimplementing infrastructure
- **Configuration System**: Easy-to-use presets with full control over all parameters
- **PyPI Ready**: Properly packaged with `pyproject.toml`, optional dependencies, and test structure

## Architecture

### Generic Infrastructure (Dataset-Agnostic)

These modules work with **any** astronomical data source:

- **`EphemerisData`** (`models.py`): Flexible container for observations (RA, DEC, magnitude, distances, custom fields)
- **`OrbitalElements`** (`models.py`): Flexible container for orbital parameters (a, e, i, Omega, w, etc.) with optional/custom fields
- **`BaseAcquisitionClient`** (`acquisition_base.py`): Abstract base for implementing dataset-specific clients
- **`BaseParser`** (`acquisition_base.py`): Abstract base for implementing dataset-specific parsers
- **`BaseTextParser`, `BaseCSVParser`, `BaseJSONParser`** (`parsers_base.py`): Mixins for common parsing patterns
- **`RateLimiter`** (`utils.py`): Generic sliding-window rate limiter
- **`ExponentialBackoff`** (`utils.py`): Generic exponential backoff calculator
- **`FileCache`** (`cache.py`): Generic file-based TTL cache with JSON serialization
- **`ClientConfig`, `CacheConfig`** (`config.py`): Generic configuration classes

### Dataset-Specific Implementations

Located in `nexuscosmos/datasets/` with submodules for each source:

#### Horizons (JPL NASA)
```
nexuscosmos/datasets/horizons/
├── __init__.py          # Public exports
├── client.py            # HorizonsClient (inherits BaseAcquisitionClient)
└── parser.py            # HorizonsParser (inherits BaseTextParser)
```

**Future Datasets**:
```
nexuscosmos/datasets/mpc/              # Minor Planet Center
nexuscosmos/datasets/gaia/             # ESA GAIA catalog
nexuscosmos/datasets/custom/           # Template for user datasets
```

## Quick Start

### Using Horizons (Current Implementation)

```python
from nexuscosmos import HorizonsClient, HorizonsQueryConfig

# Create client
client = HorizonsClient(enforce_rate_limit=True)

# Use a preset configuration
config = HorizonsQueryConfig.quick_ephemeris(object_id='1I')

# Fetch data
result = client.fetch_data(config)

# Result structure
if result['success']:
    print(f"Object: {result['object']}")
    print(f"Data: {result['data']}")
    print(f"Type: {result['ephem_type']}")
else:
    print(f"Error: {result['error']}")
```

### Custom Configuration

```python
from nexuscosmos import HorizonsQueryConfig, HorizonsClient

# Full control over parameters
config = HorizonsQueryConfig(
    object_id='1I/Oumuamua',
    start_time='2025-01-01',
    stop_time='2025-01-31',
    step_size='1d',
    observer='@399',  # Earth
    ephem_type='OBSERVER',
    quantities='1,9,20,23,24',  # RA, DEC, distance, magnitude, phase angle
    use_cache=True,
    cache_ttl_hours=24,
    enforce_rate_limit=True,
    max_requests_per_minute=10,
    timeout_seconds=30
)

client = HorizonsClient()
result = client.fetch_data(config)
```

### Available Presets

```python
from nexuscosmos import PRESETS, HorizonsQueryConfig

# Quick presets
config1 = HorizonsQueryConfig.quick_ephemeris(object_id='2I')
config2 = HorizonsQueryConfig.quick_vectors(object_id='3I')
config3 = HorizonsQueryConfig.quick_live(object_id='1I')

# Access preset configurations
for name, preset_config in PRESETS.items():
    print(f"{name}: {preset_config}")
```

## Implementing a New Dataset

To add support for a new astronomical data source (e.g., Minor Planet Center):

### 1. Create Dataset-Specific Module

```bash
mkdir -p nexuscosmos/datasets/mpc
touch nexuscosmos/datasets/mpc/__init__.py
touch nexuscosmos/datasets/mpc/client.py
touch nexuscosmos/datasets/mpc/parser.py
```

### 2. Implement Client

```python
# nexuscosmos/datasets/mpc/client.py
from nexuscosmos import BaseAcquisitionClient
import requests

class MinorPlanetCenterClient(BaseAcquisitionClient):
    """MPC-specific acquisition client."""
    
    BASE_URL = "https://minorplanetcenter.net/..."
    
    def fetch_data(self, query_config):
        """Fetch data from MPC API.
        
        Inherits caching, rate-limiting, and backoff from BaseAcquisitionClient.
        """
        # Check cache
        cache_key = self._build_cache_key(query_config)
        cached = self.get_cached_data(cache_key)
        if cached:
            return cached
        
        # Build MPC-specific request
        url = self._build_url(query_config)
        
        # Enforce rate limiting (inherited)
        if not self._rate_limited_request('mpc'):
            return {'success': False, 'error': 'Rate limited'}
        
        # Fetch and parse
        response = requests.get(url, timeout=self.timeout_seconds)
        data = self.parser.parse(response.text)
        
        # Cache result (inherited)
        self.cache_data(cache_key, data)
        
        return {'success': True, 'data': data}
```

### 3. Implement Parser

```python
# nexuscosmos/datasets/mpc/parser.py
from nexuscosmos import BaseCSVParser

class MinorPlanetCenterParser(BaseCSVParser):
    """MPC-specific CSV parser."""
    
    def parse(self, csv_text: str):
        """Parse MPC CSV format."""
        return self.parse_csv(
            csv_text,
            delimiter=' ',
            skip_rows=2,
            column_mapper={'# ID': 'object_id', 'a': 'semi_major_axis'}
        )
```

### 4. Export from Package

```python
# nexuscosmos/datasets/mpc/__init__.py
from .client import MinorPlanetCenterClient
from .parser import MinorPlanetCenterParser

__all__ = ["MinorPlanetCenterClient", "MinorPlanetCenterParser"]
```

### 5. Use New Dataset

```python
from nexuscosmos.datasets.mpc import MinorPlanetCenterClient

client = MinorPlanetCenterClient()
result = client.fetch_data(config)
```

## Data Models

### EphemerisData

Container for observations at a moment in time. Supports both standard and custom fields.

```python
from nexuscosmos import EphemerisData

# Horizons-specific data
obs = EphemerisData(
    datetime_str='2025-01-15 12:00:00',
    RA=45.5,
    DEC=30.2,
    delta=1.5,  # Distance from observer (AU)
    r=1.2,      # Heliocentric distance (AU)
    V_mag=15.5,
    elong=120.0,
    phase_angle=45.0,
    source='horizons'
)

# Custom fields for GAIA
gaia_obs = EphemerisData(
    datetime_str='2025-01-15',
    RA=45.5,
    DEC=30.2,
    source='gaia',
    extra_data={'parallax': 10.5, 'magnitude_g': 12.3}
)

# Convert to dict
data_dict = obs.to_dict()

# Safely access fields (including custom)
ra = obs.get_field('RA')
parallax = gaia_obs.get_field('parallax')
```

### OrbitalElements

Container for orbital parameters. Supports elliptical, parabolic, and hyperbolic orbits.

```python
from nexuscosmos import OrbitalElements

# Elliptical orbit (asteroid)
asteroid = OrbitalElements(
    epoch='J2000',
    a=2.5,
    e=0.1,
    i=10.0,
    Omega=45.0,
    w=90.0,
    M=180.0,
    H=15.5,
    G=0.15,
    source='horizons'
)

# Check orbit type
print(asteroid.is_elliptical())  # True
print(asteroid.is_hyperbolic())  # False

# Hyperbolic orbit (comet)
comet = OrbitalElements(
    epoch='2025-01-01',
    e=1.5,
    q=0.5,
    Tp='2025-03-15',
    source='horizons'
)

print(comet.is_hyperbolic())  # True
```

## Configuration

### HorizonsQueryConfig

Detailed control over Horizons API parameters:

```python
from nexuscosmos import HorizonsQueryConfig

config = HorizonsQueryConfig(
    object_id='1I/Oumuamua',
    start_time='2025-01-01',
    stop_time='2025-01-31',
    step_size='1d',
    observer='@399',           # Earth center
    center='@sun',             # Heliocentric
    ephem_type='OBSERVER',     # or 'VECTORS', 'ELEMENTS'
    quantities='1,9,20,23,24', # RA, DEC, distances, magnitude, phase
    use_cache=True,
    cache_ttl_hours=24,
    enforce_rate_limit=True,
    max_requests_per_minute=10,
    request_delay_seconds=1.0,
    timeout_seconds=30,
    return_raw_data=False
)

# Convert to API parameters
api_kwargs = config.to_client_kwargs()

# Print summary
print(config.summary())
```

### CacheConfig

Control caching behavior:

```python
from nexuscosmos import CacheConfig

cache_config = CacheConfig(
    enabled=True,
    ttl_seconds=86400,      # 24 hours
    cache_dir='/tmp/nexuscosmos_cache',
    clear_on_init=False
)
```

### ClientConfig

Global client settings:

```python
from nexuscosmos import ClientConfig, CacheConfig

client_config = ClientConfig(
    base_url='https://ssd.jpl.nasa.gov/api/horizons.api',
    timeout_seconds=30,
    request_delay_seconds=1.0,
    max_retries=3,
    cache=CacheConfig(enabled=True, ttl_seconds=86400),
    rate_limiting_enabled=True,
    max_requests_per_minute=10,
    verbose_logging=True
)
```

## Utilities

### Rate Limiting

```python
from nexuscosmos import RateLimiter

limiter = RateLimiter(max_attempts=10, window_minutes=1)

if limiter.is_allowed('horizons_api'):
    # Make request
    pass
else:
    retry_after = limiter.get_retry_after('horizons_api')
    print(f"Rate limited. Retry after {retry_after:.1f}s")
```

### Exponential Backoff

```python
from nexuscosmos import ExponentialBackoff
import time

backoff = ExponentialBackoff(base_delay=1.0, max_delay=60.0)

for attempt in range(5):
    try:
        # Make request
        break
    except Exception:
        delay = backoff.get_delay(attempt)
        time.sleep(delay)
```

### File Caching

```python
from nexuscosmos import FileCache

cache = FileCache(cache_dir='/tmp/cache', ttl_seconds=3600)

# Store
cache.set('horizons_1I_2025', {'data': [...], 'timestamp': ...})

# Retrieve
data = cache.get('horizons_1I_2025')

# Info
info = cache.get_cache_info('horizons_1I_2025')
print(info)  # {'hit_count': 5, 'created_at': ..., 'expires_at': ...}
```

## Installation

From PyPI (when published):

```bash
pip install nexuscosmos
```

With optional dependencies:

```bash
# Scientific utilities (astropy, pandas)
pip install "nexuscosmos[astropy,pandas]"

# Async support (httpx)
pip install "nexuscosmos[async]"

# Visualization (matplotlib, plotly)
pip install "nexuscosmos[viz]"

# Development
pip install "nexuscosmos[dev]"
```

From local development:

```bash
cd /path/to/nexuscosmos
pip install -e .
```

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=nexuscosmos

# Specific test file
pytest tests/test_basic.py
```

## Architecture Philosophy

**Generic + Dataset-Specific = Reusable Infrastructure**

NexusCosmos separates concerns:

1. **Generic Infrastructure** (core package): Rate limiting, caching, retry logic, configuration
2. **Data Models** (generic): Flexible EphemerisData and OrbitalElements for any dataset
3. **Base Classes** (abstract): Templates for implementing new dataset clients/parsers
4. **Dataset Implementations** (submodules): Horizons-specific logic isolated in `datasets/horizons/`

**Benefits**:

- Add a new dataset (MPC, GAIA) by implementing just two classes (client + parser)
- Reuse caching, rate-limiting, configuration for all datasets
- Users familiar with Horizons API can quickly learn new dataset support
- No code duplication across dataset implementations
- Clear separation of concerns for maintenance

## Future Enhancements

- [ ] Minor Planet Center (MPC) dataset support
- [ ] ESA GAIA catalog integration
- [ ] Astropy integration for high-precision time/units
- [ ] Pandas DataFrame output options
- [ ] Async/await support (httpx backend)
- [ ] Visualization utilities (matplotlib, plotly)
- [ ] Sphinx documentation
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Performance benchmarking suite

## Contributing

Contributions welcome! To add a new dataset:

1. Create `nexuscosmos/datasets/<name>/` directory
2. Implement `<name>/client.py` (inherit `BaseAcquisitionClient`)
3. Implement `<name>/parser.py` (inherit appropriate base parser)
4. Add tests in `tests/test_<name>.py`
5. Update `nexuscosmos/datasets/__init__.py` to export your classes
6. Submit PR with example usage

## License

See LICENSE file.

## Citation

If you use NexusCosmos in your research, please cite:

```bibtex
@software{nexuscosmos2025,
  author = {Pancha Narayan Sahu},
  title = {NexusCosmos: Python Library for Astroprocessing},
  year = {2025},
  url = {https://github.com/Thevishalkumar369/nexuscosmos}
}
```
