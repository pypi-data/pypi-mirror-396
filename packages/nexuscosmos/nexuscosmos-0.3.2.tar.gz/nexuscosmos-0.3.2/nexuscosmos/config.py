"""
Configuration management for astronomical data queries.

Provides both convenience defaults and full flexibility for users to control
request parameters, caching, rate-limiting, and output formats for any data source
(Horizons, MPC, GAIA, custom APIs, etc.).
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta


@dataclass
class QueryConfig:
    """Generic configuration for an astronomical data query.
    
    Sensible defaults are provided, but every field can be overridden.
    Can be used with any data source by providing appropriate parameters.
    """
    
    # Object specification
    object_id: str
    """Target object: '2I/Borisov', 'C/2019 Q4', etc."""
    
    # Time range
    start_time: str
    """ISO format start time: '2025-01-01' or '2025-01-01 12:00:00'"""
    
    stop_time: str
    """ISO format stop time: '2025-12-31' or '2025-12-31 23:59:59'"""
    
    step_size: str = "1d"
    """Time step: '1d', '1h', '30m', etc. Default: daily"""
    
    # Observer/Center
    observer: str = "@399"
    """Horizons observer code. @399=Earth geocenter. Default: @399"""
    
    center: str = "@sun"
    """Horizons center for vectors. @sun=solar system barycenter. Default: @sun"""
    
    # Query type
    ephem_type: str = "OBSERVER"
    """'OBSERVER' for RA/DEC, 'VECTORS' for x,y,z,vx,vy,vz. Default: OBSERVER"""
    
    # Output control
    quantities: str = "1,9,20,23,24"
    """Horizons QUANTITIES code (comma-sep). Default: RA,DEC,delta,r,V_mag"""
    
    # Caching
    use_cache: bool = True
    """Whether to cache results. Default: True"""
    
    cache_ttl_hours: int = 24
    """Cache time-to-live in hours. Default: 24 hours"""
    
    # Rate limiting
    enforce_rate_limit: bool = True
    """Enforce rate limiting. Default: True"""
    
    max_requests_per_minute: int = 10
    """Max API requests per minute. Default: 10"""
    
    request_delay_seconds: float = 1.0
    """Minimum delay between requests. Default: 1.0 second"""
    
    # HTTP
    timeout_seconds: int = 30
    """HTTP request timeout. Default: 30 seconds"""
    
    # Output format
    return_raw_data: bool = False
    """Include raw API response text. Default: False (saves memory)"""
    
    @classmethod
    def quick_ephemeris(
        cls,
        object_id: str,
        start_time: str,
        stop_time: str,
        observer: str = "@399"
    ) -> "QueryConfig":
        """Quick preset: observer/object ephemeris with sensible defaults.
        
        Args:
            object_id: Target object ID
            start_time: ISO date/datetime
            stop_time: ISO date/datetime
            observer: Observer code (default: Earth @399 for Horizons)
        
        Returns:
            QueryConfig ready for use
        
        Example:
            config = QueryConfig.quick_ephemeris(
                "2I/Borisov", "2025-01-01", "2025-01-31"
            )
        """
        return cls(
            object_id=object_id,
            start_time=start_time,
            stop_time=stop_time,
            observer=observer,
            ephem_type="OBSERVER"
        )
    
    @classmethod
    def quick_vectors(
        cls,
        object_id: str,
        start_time: str,
        stop_time: str,
        center: str = "@sun"
    ) -> "QueryConfig":
        """Quick preset: state vectors with sensible defaults.
        
        Args:
            object_id: Target object ID
            start_time: ISO date/datetime
            stop_time: ISO date/datetime
            center: Reference frame center (default: sun @sun for Horizons)
        
        Returns:
            QueryConfig ready for use
        
        Example:
            config = QueryConfig.quick_vectors(
                "2I/Borisov", "2025-01-01", "2025-01-31"
            )
        """
        return cls(
            object_id=object_id,
            start_time=start_time,
            stop_time=stop_time,
            center=center,
            ephem_type="VECTORS"
        )
    
    @classmethod
    def quick_live(cls, object_id: str, observer: str = "@399") -> "QueryConfig":
        """Quick preset: fetch current position (live mode).
        
        Auto-sets start_time to now and stop_time to 1 hour from now.
        
        Args:
            object_id: Target object ID
            observer: Observer code (default: Earth @399 for Horizons)
        
        Returns:
            QueryConfig ready for use
        
        Example:
            config = QueryConfig.quick_live("2I/Borisov")
        """
        now = datetime.utcnow()
        start = now.strftime("%Y-%m-%d %H:%M")
        stop = (now + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        
        return cls(
            object_id=object_id,
            start_time=start,
            stop_time=stop,
            observer=observer,
            step_size="1h",
            ephem_type="OBSERVER"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict (useful for debugging/logging)."""
        return asdict(self)
    
    def to_client_kwargs(self) -> Dict[str, Any]:
        """Extract client method parameters (for internal use)."""
        if self.ephem_type == "OBSERVER":
            return {
                "object_id": self.object_id,
                "start_time": self.start_time,
                "stop_time": self.stop_time,
                "step_size": self.step_size,
                "observer": self.observer,
            }
        else:  # VECTORS
            return {
                "object_id": self.object_id,
                "start_time": self.start_time,
                "stop_time": self.stop_time,
                "step_size": self.step_size,
                "center": self.center,
            }
    
    def summary(self) -> str:
        """Human-readable summary of the query."""
        lines = [
            f"Object: {self.object_id}",
            f"Query Type: {self.ephem_type}",
            f"Period: {self.start_time} to {self.stop_time}",
            f"Step: {self.step_size}",
            f"Cache: {'enabled' if self.use_cache else 'disabled'}",
            f"Rate Limit: {self.max_requests_per_minute} req/min" if self.enforce_rate_limit else "Rate Limit: disabled",
        ]
        return "\n".join(lines)


@dataclass
class CacheConfig:
    """Configuration for caching behavior."""
    
    enabled: bool = True
    """Enable/disable caching globally. Default: True"""
    
    ttl_seconds: int = 86400
    """Cache entry time-to-live in seconds. Default: 24 hours"""
    
    cache_dir: Optional[str] = None
    """Cache directory path. Default: ./.nexuscache"""
    
    clear_on_init: bool = False
    """Clear cache on client initialization. Default: False"""


@dataclass
class ClientConfig:
    """Global configuration for a generic data acquisition client.
    
    This is a template for dataset-specific clients. Subclasses should override
    base_url and other parameters for their specific data source.
    """
    
    base_url: Optional[str] = None
    """Data source API endpoint. Set by subclass or passed as parameter."""
    
    timeout_seconds: int = 30
    """HTTP request timeout. Default: 30 seconds"""
    
    request_delay_seconds: float = 1.0
    """Minimum delay between requests. Default: 1.0 second"""
    
    max_retries: int = 3
    """Number of retry attempts on failure. Default: 3"""
    
    cache: CacheConfig = field(default_factory=CacheConfig)
    """Caching configuration"""
    
    rate_limiting_enabled: bool = True
    """Enable rate limiting. Default: True"""
    
    max_requests_per_minute: int = 10
    """Max API requests per minute. Default: 10"""
    
    verbose_logging: bool = False
    """Enable verbose logging. Default: False"""


# Preset configurations for common use cases
PRESETS = {
    "default": {
        "description": "Standard observer ephemeris query",
        "ephem_type": "OBSERVER",
        "step_size": "1d",
        "observer": "@399",
    },
    "highres": {
        "description": "High-resolution hourly ephemeris",
        "ephem_type": "OBSERVER",
        "step_size": "1h",
        "observer": "@399",
    },
    "vectors": {
        "description": "Heliocentric state vectors (position + velocity)",
        "ephem_type": "VECTORS",
        "step_size": "1d",
        "center": "@sun",
    },
    "live": {
        "description": "Current position (1-hour window, hourly steps)",
        "ephem_type": "OBSERVER",
        "step_size": "1h",
        "observer": "@399",
        "duration_hours": 1,
    },
}
