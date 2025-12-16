"""
Generic data models for astronomical observations and orbital mechanics.

These models are dataset-agnostic and can be used with any data source
(JPL Horizons, NASA GAIA, Minor Planet Center, etc.). They provide a
flexible structure for storing ephemeris and orbital data.
"""
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List


@dataclass
class EphemerisData:
    """Generic ephemeris record: position, magnitude, distances at a moment in time.
    
    Flexible fields allow use with any dataset. Users populate only fields
    relevant to their data source.
    
    Example (JPL Horizons):
        - datetime_str, datetime_jd, RA, DEC, delta, r, V_mag all populated
    
    Example (GAIA):
        - datetime_str, RA, DEC, parallax (instead of distances)
    
    Example (Custom):
        - Any subset or superset of fields via extra_data dict
    """
    
    # Core astrometric fields (populated by most datasets)
    datetime_str: str
    """ISO format datetime or date string"""
    
    RA: float
    """Right Ascension in degrees (or radians if specified in metadata)"""
    
    DEC: float
    """Declination in degrees (or radians if specified in metadata)"""
    
    # Time reference (optional, dataset-dependent)
    datetime_jd: Optional[float] = None
    """Julian Date (if available from source)"""
    
    # Solar System distances (optional, Horizons-specific but common)
    delta: Optional[float] = None
    """Distance from observer (typically Earth), in AU"""
    
    r: Optional[float] = None
    """Heliocentric distance (Sun-object), in AU"""
    
    # Magnitude (optional, most datasets have this)
    V_mag: Optional[float] = None
    """Visual magnitude (or any magnitude if source specifies)"""
    
    # Horizons-specific (optional)
    elong: Optional[float] = None
    """Solar elongation (degrees) - Horizons specific"""
    
    phase_angle: Optional[float] = None
    """Sun-Observer-Target phase angle (degrees) - Horizons specific"""
    
    # Position in Cartesian coords (optional, useful for propagation)
    x: Optional[float] = None
    """Heliocentric X coordinate (AU)"""
    
    y: Optional[float] = None
    """Heliocentric Y coordinate (AU)"""
    
    z: Optional[float] = None
    """Heliocentric Z coordinate (AU)"""
    
    # Velocity (optional)
    vx: Optional[float] = None
    """Heliocentric velocity X (AU/day or other units per metadata)"""
    
    vy: Optional[float] = None
    """Heliocentric velocity Y (AU/day or other units per metadata)"""
    
    vz: Optional[float] = None
    """Heliocentric velocity Z (AU/day or other units per metadata)"""
    
    # Metadata for interpretation
    source: str = "unknown"
    """Data source identifier: 'horizons', 'gaia', 'minor_planet_center', etc."""
    
    units: Dict[str, str] = field(default_factory=dict)
    """Units for each field, e.g., {'delta': 'AU', 'RA': 'degrees', 'vx': 'AU/day'}"""
    
    # Extensibility: any dataset-specific fields
    extra_data: Dict[str, Any] = field(default_factory=dict)
    """Catch-all for dataset-specific fields not in standard fields"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)
    
    def get_field(self, name: str, default: Any = None) -> Any:
        """Safely get a field, checking both standard and extra_data.
        
        Args:
            name: Field name (e.g., 'RA', 'custom_field')
            default: Value to return if field not found
        
        Returns:
            Field value or default
        """
        if hasattr(self, name):
            return getattr(self, name)
        return self.extra_data.get(name, default)


@dataclass
class OrbitalElements:
    """Generic orbital elements: semi-major axis, eccentricity, inclination, etc.
    
    Flexible fields support classical Keplerian elements, cometary orbits,
    hyperbolic orbits, and variations from different sources.
    
    Example (Elliptical):
        - a=2.5, e=0.1, i=10, Omega=45, w=90, M=180, period=4.0 years
    
    Example (Hyperbolic from Horizons):
        - a=None, e=1.5, q=0.5, Tp='2025-01-15', period=None
    
    Example (Minor Planet Center):
        - a, e, i, Omega, w, M, H (absolute magnitude), G (slope param)
    """
    
    # Epoch of elements
    epoch: str
    """Reference epoch for elements, ISO format or 'J2000', 'JD 2460000.0', etc."""
    
    # Semi-major axis (None for hyperbolic orbits)
    a: Optional[float] = None
    """Semi-major axis (AU) - None for hyperbolic (e > 1)"""
    
    # Eccentricity (defines orbit shape)
    e: float = 0.0
    """Eccentricity: 0=circular, 0<e<1=elliptical, e=1=parabolic, e>1=hyperbolic"""
    
    # Angular elements (in degrees)
    i: float = 0.0
    """Inclination (degrees)"""
    
    Omega: float = 0.0
    """Longitude of ascending node (degrees)"""
    
    w: float = 0.0
    """Argument of periapsis (degrees)"""
    
    # Alternative parameterizations
    q: Optional[float] = None
    """Perihelion distance (AU) - useful for comets"""
    
    Q: Optional[float] = None
    """Aphelion distance (AU)"""
    
    Tp: Optional[str] = None
    """Time of perihelion passage (ISO or JD)"""
    
    # Mean motion / orbital period
    n: Optional[float] = None
    """Mean motion (degrees/day)"""
    
    M: Optional[float] = None
    """Mean anomaly at epoch (degrees)"""
    
    period: Optional[float] = None
    """Orbital period: days for elliptical, None for hyperbolic"""
    
    # Magnitude parameters (for brightness estimation)
    H: Optional[float] = None
    """Absolute magnitude (standard distance for comparison)"""
    
    G: Optional[float] = None
    """Magnitude slope parameter (for phase angle effects)"""
    
    # Metadata
    source: str = "unknown"
    """Data source: 'horizons', 'mpc', 'jpl_small_bodies', etc."""
    
    units: Dict[str, str] = field(default_factory=dict)
    """Units specification, e.g., {'a': 'AU', 'i': 'degrees', 'period': 'days'}"""
    
    # Extensibility
    extra_data: Dict[str, Any] = field(default_factory=dict)
    """Dataset-specific orbital parameters not in standard fields"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)
    
    def is_hyperbolic(self) -> bool:
        """Check if orbit is hyperbolic (e > 1)."""
        return self.e > 1.0
    
    def is_parabolic(self) -> bool:
        """Check if orbit is parabolic (e ≈ 1)."""
        return abs(self.e - 1.0) < 0.001
    
    def is_elliptical(self) -> bool:
        """Check if orbit is elliptical (0 < e < 1)."""
        return 0.0 < self.e < 1.0
    
    def is_circular(self) -> bool:
        """Check if orbit is approximately circular (e ≈ 0)."""
        return self.e < 0.05
    
    def get_field(self, name: str, default: Any = None) -> Any:
        """Safely get a field, checking both standard and extra_data.
        
        Args:
            name: Field name (e.g., 'a', 'custom_param')
            default: Value to return if field not found
        
        Returns:
            Field value or default
        """
        if hasattr(self, name):
            return getattr(self, name)
        return self.extra_data.get(name, default)

