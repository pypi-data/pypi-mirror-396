"""
Basic tests for nexuscosmos library.

Run with: pytest tests/test_basic.py
"""
import pytest
from nexuscosmos import (
    EphemerisData,
    OrbitalElements,
    HorizonsClient,
    HorizonsParser,
    RateLimiter,
    ExponentialBackoff,
    FileCache,
)


class TestModels:
    def test_ephemeris_data_creation(self):
        ephem = EphemerisData(
            datetime_str="2025-01-15 12:00:00",
            datetime_jd=2460700.0,
            RA=45.5,
            DEC=30.2,
            delta=1.5,
            r=1.2,
            x=0.9,
            y=0.8,
            z=0.7,
            vx=0.01,
            vy=-0.005,
            vz=0.002,
            V_mag=15.5,
        )
        assert ephem.datetime_str == "2025-01-15 12:00:00"
        assert ephem.RA == 45.5
        assert ephem.V_mag == 15.5

    def test_ephemeris_to_dict(self):
        ephem = EphemerisData(
            datetime_str="2025-01-15",
            datetime_jd=2460700.0,
            RA=45.5,
            DEC=30.2,
            delta=1.5,
            r=1.2,
            x=0.9,
            y=0.8,
            z=0.7,
            vx=0.01,
            vy=-0.005,
            vz=0.002,
        )
        d = ephem.to_dict()
        assert isinstance(d, dict)
        assert d["RA"] == 45.5

    def test_orbital_elements_creation(self):
        oe = OrbitalElements(epoch="2025-01-15", a=2.5, e=0.95, i=35.0, Omega=45.0, w=90.0, q=0.125, H=10.5)
        assert oe.epoch == "2025-01-15"
        assert oe.e == 0.95
        assert not oe.is_hyperbolic()

    def test_orbital_elements_hyperbolic(self):
        oe = OrbitalElements(epoch="2025-01-15", e=1.5)
        assert oe.is_hyperbolic()


class TestParser:
    def test_parse_observer_ephemeris_empty(self):
        parser = HorizonsParser()
        raw_data = "No data markers"
        result = parser.parse_observer_ephemeris(raw_data)
        assert result == []

    def test_parse_observer_ephemeris_minimal(self):
        parser = HorizonsParser()
        raw_data = """
$$SOE
2025-01-15 12:00:00, 45.5, 30.2, 1.5, 1.2, 15.5, 120.0, 45.0
$$EOE
"""
        result = parser.parse_observer_ephemeris(raw_data)
        assert len(result) == 1
        assert result[0]["RA"] == 45.5
        assert result[0]["DEC"] == 30.2

    def test_parse_state_vectors_empty(self):
        parser = HorizonsParser()
        raw_data = "No data markers"
        result = parser.parse_state_vectors(raw_data)
        assert result == []

    def test_parse_state_vectors_minimal(self):
        parser = HorizonsParser()
        raw_data = """
$$SOE
2460700.0, 0.9, 0.8, 0.7, 0.01, -0.005, 0.002
$$EOE
"""
        result = parser.parse_state_vectors(raw_data)
        assert len(result) == 1
        assert result[0]["x"] == 0.9
        assert result[0]["vx"] == 0.01

    def test_parse_orbital_elements(self):
        parser = HorizonsParser()
        raw_data = """
EC= 0.956, A= 2.5, IN= 35.0, OM= 45.0, W= 90.0, QR= 0.125
"""
        result = parser.parse_orbital_elements(raw_data)
        assert pytest.approx(result["e"], rel=1e-6) == 0.956
        assert pytest.approx(result["a"], rel=1e-6) == 2.5


class TestRateLimiter:
    def test_rate_limiter_allow_under_limit(self):
        limiter = RateLimiter(max_attempts=3, window_minutes=1)
        assert limiter.is_allowed("test_id")
        assert limiter.is_allowed("test_id")
        assert limiter.is_allowed("test_id")

    def test_rate_limiter_block_over_limit(self):
        limiter = RateLimiter(max_attempts=2, window_minutes=1)
        assert limiter.is_allowed("test_id")
        assert limiter.is_allowed("test_id")
        assert not limiter.is_allowed("test_id")

    def test_rate_limiter_reset(self):
        limiter = RateLimiter(max_attempts=1, window_minutes=1)
        assert limiter.is_allowed("test_id")
        assert not limiter.is_allowed("test_id")
        limiter.reset("test_id")
        assert limiter.is_allowed("test_id")


class TestExponentialBackoff:
    def test_backoff_get_delay(self):
        backoff = ExponentialBackoff(base_delay=1.0, max_delay=60.0, multiplier=2.0)
        assert backoff.get_delay(0) == 1.0
        assert backoff.get_delay(1) == 2.0
        assert backoff.get_delay(2) == 4.0
        assert backoff.get_delay(10) == 60.0

    def test_backoff_max_delay_capped(self):
        """Test that delay is capped at max_delay."""
        backoff = ExponentialBackoff(base_delay=1.0, max_delay=10.0, multiplier=2.0)
        # attempt 10 would be 1024 without cap
        assert backoff.get_delay(10) == 10.0

    def test_backoff_custom_multiplier(self):
        """Test custom multiplier."""
        backoff = ExponentialBackoff(base_delay=1.0, max_delay=100.0, multiplier=3.0)
        assert backoff.get_delay(0) == 1.0
        assert backoff.get_delay(1) == 3.0
        assert backoff.get_delay(2) == 9.0


class TestHorizonsClient:
    def test_client_initialization(self):
        client = HorizonsClient()
        assert client.base_url == "https://ssd.jpl.nasa.gov/api/horizons.api"
        assert client.timeout_seconds == 30.0

    def test_resolve_designation(self):
        client = HorizonsClient()
        assert client._resolve_designation("2I/Borisov") == "C/2019 Q4"
        assert client._resolve_designation("C/2019 Q4") == "C/2019 Q4"


class TestFileCache:
    def test_cache_set_get(self, tmp_path):
        cache = FileCache(cache_dir=str(tmp_path), ttl_seconds=3600)
        test_data = {"test": "data", "value": 42}
        cache.set("test_key", test_data)
        retrieved = cache.get("test_key")
        assert retrieved == test_data

    def test_cache_miss(self, tmp_path):
        cache = FileCache(cache_dir=str(tmp_path))
        assert cache.get("nonexistent") is None

    def test_cache_invalidate(self, tmp_path):
        cache = FileCache(cache_dir=str(tmp_path))
        cache.set("key1", {"data": 1})
        cache.invalidate("key1")
        assert cache.get("key1") is None

    def test_cache_info(self, tmp_path):
        cache = FileCache(cache_dir=str(tmp_path))
        cache.set("key1", {"data": 1})
        cache.set("key2", {"data": 2})
        info = cache.get_cache_info()
        assert info['entry_count'] >= 2
        assert info['ttl_seconds'] == 86400
