"""
Generic base classes for parsing astronomical data from various sources.

Supports common parsing patterns (CSV, text with markers, JSON) that can be
inherited by dataset-specific parsers. The goal is to reduce code duplication
when adding new data sources.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import re
import csv
from io import StringIO


class BaseTextParser(ABC):
    """Abstract base for parsing text-based astronomical data.
    
    Useful for datasets that return plaintext responses with structured sections
    (like JPL Horizons with $$SOE/$$EOE markers).
    """
    
    @staticmethod
    def _safe_float(value: str, default: Optional[float] = None) -> Optional[float]:
        """Safely convert string to float.
        
        Args:
            value: String to convert
            default: Value to return if conversion fails
        
        Returns:
            Parsed float or default
        """
        try:
            return float(value.strip())
        except (ValueError, AttributeError):
            return default
    
    @staticmethod
    def _safe_str(value: Any, default: str = "") -> str:
        """Safely convert value to string.
        
        Args:
            value: Value to convert
            default: Default string if value is None
        
        Returns:
            String representation or default
        """
        if value is None:
            return default
        return str(value).strip()
    
    @abstractmethod
    def parse(self, raw_text: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Parse raw text response.
        
        Args:
            raw_text: Raw text response from data source
        
        Returns:
            Parsed data structure
        """
        pass
    
    def extract_section(
        self, text: str, start_marker: str, end_marker: str
    ) -> Optional[str]:
        """Extract section of text between two markers.
        
        Args:
            text: Full text
            start_marker: Opening marker (e.g., '$$SOE')
            end_marker: Closing marker (e.g., '$$EOE')
        
        Returns:
            Section text or None if markers not found
        """
        pattern = rf"{re.escape(start_marker)}(.*?){re.escape(end_marker)}"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None
    
    def parse_lines(
        self, text: str, parser_func
    ) -> List[Dict[str, Any]]:
        """Parse multiple lines of text using a line parser function.
        
        Args:
            text: Multi-line text
            parser_func: Function(line: str) -> Dict[str, Any]
        
        Returns:
            List of parsed dictionaries
        """
        records = []
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            try:
                record = parser_func(line)
                if record:
                    records.append(record)
            except Exception:
                # Skip lines that fail to parse
                continue
        return records


class BaseCSVParser(ABC):
    """Abstract base for parsing CSV-formatted astronomical data.
    
    Useful for datasets that return CSV format (Minor Planet Center, GAIA).
    """
    
    @abstractmethod
    def parse(self, csv_text: str) -> List[Dict[str, Any]]:
        """Parse CSV data.
        
        Args:
            csv_text: CSV-formatted text
        
        Returns:
            List of dictionaries (one per row)
        """
        pass
    
    def parse_csv(
        self,
        csv_text: str,
        delimiter: str = ',',
        skip_rows: int = 0,
        column_mapper: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """Generic CSV parsing with optional column mapping.
        
        Args:
            csv_text: CSV-formatted text
            delimiter: Column delimiter (default: ',')
            skip_rows: Number of header rows to skip
            column_mapper: Dict mapping CSV column names to output names
                          (e.g., {'# Object': 'object_id'})
        
        Returns:
            List of dictionaries with mapped column names
        """
        records = []
        lines = csv_text.strip().split('\n')
        
        # Skip header rows
        if skip_rows > 0:
            lines = lines[skip_rows:]
        
        reader = csv.DictReader(lines, delimiter=delimiter)
        for row in reader:
            if column_mapper:
                # Rename columns according to mapper
                mapped_row = {}
                for csv_col, value in row.items():
                    output_col = column_mapper.get(csv_col, csv_col)
                    mapped_row[output_col] = value
                records.append(mapped_row)
            else:
                records.append(row)
        
        return records


class BaseJSONParser(ABC):
    """Abstract base for parsing JSON-formatted astronomical data.
    
    Useful for datasets that return JSON (GAIA, some modern APIs).
    """
    
    @abstractmethod
    def parse(self, json_data: Dict[str, Any]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Parse JSON data structure.
        
        Args:
            json_data: Parsed JSON object (dict or list)
        
        Returns:
            Extracted/transformed data
        """
        pass
    
    @staticmethod
    def extract_records(json_data: Any, path: str) -> List[Dict[str, Any]]:
        """Extract list of records from nested JSON using dot notation.
        
        Args:
            json_data: JSON data structure
            path: Dot-separated path (e.g., 'data.objects' or 'results')
        
        Returns:
            List of records
        """
        keys = path.split('.')
        current = json_data
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list):
                # If it's a list, apply to all elements
                current = [item.get(key) if isinstance(item, dict) else None for item in current]
            else:
                return []
        
        if isinstance(current, list):
            return current
        elif isinstance(current, dict):
            return [current]
        return []


class CompositeParser:
    """Combines multiple parsers for flexible format support.
    
    Allows a client to attempt parsing with multiple formats (JSON first,
    then fallback to CSV, then text) without explicit format detection.
    """
    
    def __init__(self, parsers: List[Any]):
        """Initialize with ordered list of parsers to try.
        
        Args:
            parsers: List of parser instances with parse() method
        """
        self.parsers = parsers
    
    def parse_auto(self, raw_data: Any) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Try parsing with each parser until one succeeds.
        
        Args:
            raw_data: Raw response data (string or object)
        
        Returns:
            Parsed data from first successful parser
        
        Raises:
            ValueError: If no parser succeeds
        """
        errors = []
        for parser in self.parsers:
            try:
                result = parser.parse(raw_data)
                if result:
                    return result
            except Exception as e:
                errors.append(f"{parser.__class__.__name__}: {str(e)}")
        
        raise ValueError(f"All parsers failed: {'; '.join(errors)}")
