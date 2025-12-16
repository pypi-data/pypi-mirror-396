"""
JPL Horizons-specific text parser inheriting from BaseTextParser.

Handles Horizons' distinctive $$SOE/$$EOE markers and text-based formats.

Example:
    parser = HorizonsParser()
    ephemeris_list = parser.parse_observer_ephemeris(raw_response_text)
    state_vectors = parser.parse_state_vectors(raw_response_text)
    orbital_elements = parser.parse_orbital_elements(raw_response_text)
"""

from typing import List, Dict, Any, Optional
import re
from datetime import datetime

from ...parsers_base import BaseTextParser


class HorizonsParser(BaseTextParser):
    """Horizons-specific text parser for API responses.
    
    Handles Horizons' $$SOE/$$EOE marker format for sections and
    provides methods for parsing observer ephemeris, state vectors,
    and orbital elements.
    """
    
    def parse(self, raw_text: str) -> Dict[str, Any]:
        """Generic parse (intended for single-section responses).
        
        For Horizons, consider calling parse_observer_ephemeris,
        parse_state_vectors, or parse_orbital_elements directly.
        
        Args:
            raw_text: Full Horizons response
        
        Returns:
            Parsed result (format depends on content detected)
        """
        # Try to detect response type and parse accordingly
        if "jd" in raw_text.lower() and "x" in raw_text.lower():
            return {"state_vectors": self.parse_state_vectors(raw_text)}
        elif "ra" in raw_text.lower() and "dec" in raw_text.lower():
            return {"ephemeris": self.parse_observer_ephemeris(raw_text)}
        else:
            return {"orbital_elements": self.parse_orbital_elements(raw_text)}
    
    def parse_observer_ephemeris(self, raw_text: str) -> List[Dict[str, Any]]:
        """Parse observer-based ephemeris from Horizons response.
        
        Extracts data between $$SOE and $$EOE markers, expecting rows like:
        "2025-01-15 12:00, 45.5, 30.2, 1.5, 1.2, 15.5, 120.0, 45.0"
        
        Columns: datetime_str, RA, DEC, delta, r, V_mag, elong, phase_angle
        
        Args:
            raw_text: Raw Horizons text response
        
        Returns:
            List of ephemeris record dictionaries
        """
        section = self.extract_section(raw_text, "$$SOE", "$$EOE")
        if not section:
            return []
        
        records = []
        for line in section.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Split on comma and clean
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 3:
                continue
            
            try:
                record = {
                    "datetime_str": parts[0],
                    "RA": self._safe_float(parts[1]),
                    "DEC": self._safe_float(parts[2]),
                    "delta": self._safe_float(parts[3]) if len(parts) > 3 else None,
                    "r": self._safe_float(parts[4]) if len(parts) > 4 else None,
                    "V_mag": self._safe_float(parts[5]) if len(parts) > 5 else None,
                    "elong": self._safe_float(parts[6]) if len(parts) > 6 else None,
                    "phase_angle": self._safe_float(parts[7]) if len(parts) > 7 else None,
                }
                records.append(record)
            except (ValueError, IndexError):
                continue
        
        return records
    
    def parse_state_vectors(self, raw_text: str) -> List[Dict[str, Any]]:
        """Parse heliocentric state vectors from Horizons response.
        
        Extracts data between $$SOE and $$EOE markers, expecting rows like:
        "2460700.0, 0.9, 0.8, 0.7, 0.01, -0.005, 0.002"
        
        Columns: jd, x, y, z, vx, vy, vz (AU and AU/day)
        
        Args:
            raw_text: Raw Horizons text response
        
        Returns:
            List of state vector record dictionaries
        """
        section = self.extract_section(raw_text, "$$SOE", "$$EOE")
        if not section:
            return []
        
        records = []
        for line in section.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 7:
                continue
            
            try:
                record = {
                    "jd": self._safe_float(parts[0]),
                    "x": self._safe_float(parts[1]),
                    "y": self._safe_float(parts[2]),
                    "z": self._safe_float(parts[3]),
                    "vx": self._safe_float(parts[4]),
                    "vy": self._safe_float(parts[5]),
                    "vz": self._safe_float(parts[6]),
                }
                records.append(record)
            except (ValueError, IndexError):
                continue
        
        return records
    
    def parse_orbital_elements(self, raw_text: str) -> Dict[str, Any]:
        """Parse orbital elements from Horizons response.
        
        Extracts key=value pairs, normalizing various Horizons labels:
        - EC/E -> e (eccentricity)
        - A -> a (semi-major axis)
        - IN -> i (inclination)
        - OM -> Omega (longitude ascending node)
        - W -> w (argument of periapsis)
        - QR/Q -> q (perihelion distance)
        - Tp -> Tp (perihelion time)
        - MA -> M (mean anomaly)
        - N -> n (mean motion)
        - H -> H (absolute magnitude)
        - G -> G (slope parameter)
        
        Args:
            raw_text: Raw Horizons text response
        
        Returns:
            Dictionary of parsed orbital elements
        """
        result = {}
        
        # Split on commas and newlines to find key=value pairs
        for token in re.split(r'[,\n]', raw_text):
            token = token.strip()
            if not token:
                continue
            
            # Look for "KEY = VALUE" or "KEY= VALUE" patterns
            match = re.match(r'([A-Za-z]+)\s*=\s*([0-9eE+\-\.]+)', token)
            if not match:
                continue
            
            key = match.group(1).upper()
            value = self._safe_float(match.group(2))
            if value is None:
                continue
            
            # Normalize Horizons keys to standard orbital element names
            if key in ("EC", "E"):
                result["e"] = value
            elif key == "A":
                result["a"] = value
            elif key == "IN":
                result["i"] = value
            elif key == "OM":
                result["Omega"] = value
            elif key == "W":
                result["w"] = value
            elif key in ("QR", "Q"):
                result["q"] = value
            elif key == "TP":
                result["Tp"] = match.group(2)  # Keep as string
            elif key == "MA":
                result["M"] = value
            elif key == "N":
                result["n"] = value
            elif key == "H":
                result["H"] = value
            elif key == "G":
                result["G"] = value
            elif key == "PERIOD":
                result["period"] = value
        
        return result
