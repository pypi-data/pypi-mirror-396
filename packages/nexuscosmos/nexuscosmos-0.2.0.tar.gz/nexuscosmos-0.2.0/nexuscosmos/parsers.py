"""
Simple, dependency-free parsers for astronomical data text responses.

These parsers are intentionally lightweight and defensive. They are
placeholders until the project integrates `astropy`/`pandas` for
high-precision time and unit handling.
"""
from typing import List, Dict, Any
import re
from datetime import datetime


def _safe_float(s: str, default: float = None):
    try:
        return float(s)
    except Exception:
        return default


class HorizonsParser:
    """Parser helpers for Horizons text output.

    Methods return lists of dicts or dicts with parsed numeric values.
    They are not exhaustive parsers for all Horizons options, but cover
    the primary outputs used by the package (observer ephemeris,
    state vectors, orbital elements).
    """

    @staticmethod
    def _extract_soe(text: str) -> List[str]:
        """Return list of lines between $$SOE and $$EOE markers (all blocks)."""
        blocks = []
        for match in re.finditer(r"\$\$SOE(.*?)\$\$EOE", text, re.S | re.M):
            body = match.group(1).strip()
            if body:
                blocks.extend([ln.strip() for ln in body.splitlines() if ln.strip()])
        return blocks

    @classmethod
    def parse_observer_ephemeris(cls, raw: str) -> List[Dict[str, Any]]:
        """Parse a simple observer ephemeris CSV-like block.

        Expected minimal row format (example used by package tests):
        "2025-01-15 12:00:00, 45.5, 30.2, 1.5, 1.2, 15.5, 120.0, 45.0"
        mapping -> datetime_str, RA, DEC, delta, r, V_mag, elong, ???
        """
        lines = cls._extract_soe(raw)
        out = []
        for ln in lines:
            parts = [p.strip() for p in ln.split(",") if p.strip()]
            if len(parts) < 3:
                continue
            dt = parts[0]
            RA = _safe_float(parts[1])
            DEC = _safe_float(parts[2])
            delta = _safe_float(parts[3]) if len(parts) > 3 else None
            r = _safe_float(parts[4]) if len(parts) > 4 else None
            V_mag = _safe_float(parts[5]) if len(parts) > 5 else None
            elong = _safe_float(parts[6]) if len(parts) > 6 else None

            out.append({
                "datetime_str": dt,
                "RA": RA,
                "DEC": DEC,
                "delta": delta,
                "r": r,
                "V_mag": V_mag,
                "elong": elong,
            })
        return out

    @classmethod
    def parse_state_vectors(cls, raw: str) -> List[Dict[str, Any]]:
        """Parse state vectors (JD, x, y, z, vx, vy, vz).

        Minimal expected row: "2460700.0, 0.9, 0.8, 0.7, 0.01, -0.005, 0.002"
        """
        lines = cls._extract_soe(raw)
        out = []
        for ln in lines:
            parts = [p.strip() for p in ln.split(",") if p.strip()]
            if len(parts) < 7:
                continue
            jd = _safe_float(parts[0])
            x = _safe_float(parts[1])
            y = _safe_float(parts[2])
            z = _safe_float(parts[3])
            vx = _safe_float(parts[4])
            vy = _safe_float(parts[5])
            vz = _safe_float(parts[6])

            out.append({"jd": jd, "x": x, "y": y, "z": z, "vx": vx, "vy": vy, "vz": vz})
        return out

    @staticmethod
    def parse_orbital_elements(raw: str) -> Dict[str, Any]:
        """Parse a simple line with key=value pairs for orbital elements.

        Example: "EC= 0.956, A= 2.5, IN= 35.0, OM= 45.0, W= 90.0, QR= 0.125"
        Returns a dict with keys like 'e','a','i','Omega','w','q'.
        """
        out = {}
        for token in re.split(r"[\,\n]", raw):
            token = token.strip()
            if not token:
                continue
            m = re.match(r"([A-Za-z]+)\s*=\s*([0-9eE+\-.]+)", token)
            if not m:
                continue
            key, val = m.group(1).upper(), m.group(2)
            num = _safe_float(val)
            if key in ("EC", "E"):
                out["e"] = num
            elif key in ("A",):
                out["a"] = num
            elif key in ("IN",):
                out["i"] = num
            elif key in ("OM",):
                out["Omega"] = num
            elif key in ("W",):
                out["w"] = num
            elif key in ("QR", "Q",):
                out["q"] = num
        return out

    @staticmethod
    def _extract_jd_from_date(date_str: str) -> float:
        """Attempt to extract JD from an ISO date; fallback to 0.0."""
        try:
            dt = datetime.fromisoformat(date_str)
            a = (14 - dt.month) // 12
            y = dt.year + 4800 - a
            m = dt.month + 12 * a - 3
            jd = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
            return float(jd)
        except Exception:
            return 0.0
