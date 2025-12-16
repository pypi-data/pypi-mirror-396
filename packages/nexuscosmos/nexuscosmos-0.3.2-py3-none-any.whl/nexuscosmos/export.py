"""
Data export utilities for astronomical observations.

Convert query results to various formats (CSV, JSON, DataFrame, etc.)
"""
import json
import csv
import io
from typing import Dict, Any, List, Optional, Union


class DataExporter:
    """Export astronomical data to various formats."""
    
    @staticmethod
    def to_dict(result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data as dictionary.
        
        Args:
            result: Result dict from fetch_data()
        
        Returns:
            Data portion of result
        """
        if not result.get('success'):
            raise ValueError(f"Cannot export failed result: {result.get('error')}")
        return result.get('data', {})
    
    @staticmethod
    def to_json(result: Dict[str, Any], indent: int = 2) -> str:
        """Export to JSON string.
        
        Args:
            result: Result dict from fetch_data()
            indent: JSON indentation (None for compact)
        
        Returns:
            JSON string
        
        Example:
            client = HorizonsClient()
            result = client.fetch_data(config)
            json_str = DataExporter.to_json(result)
            print(json_str)
        """
        if not result.get('success'):
            raise ValueError(f"Cannot export failed result: {result.get('error')}")
        
        data = result.get('data', {})
        return json.dumps(data, indent=indent, default=str)
    
    @staticmethod
    def to_csv(result: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """Export to CSV format.
        
        Args:
            result: Result dict from fetch_data()
            output_file: Optional file path to write to
        
        Returns:
            CSV string (or writes to file if output_file provided)
        
        Example:
            client = HorizonsClient()
            result = client.fetch_data(config)
            csv_str = DataExporter.to_csv(result)
            # Or write directly:
            DataExporter.to_csv(result, 'data.csv')
        """
        if not result.get('success'):
            raise ValueError(f"Cannot export failed result: {result.get('error')}")
        
        data = result.get('data', {})
        
        # Handle both list and dict responses
        if isinstance(data, list):
            rows = data
        elif isinstance(data, dict):
            rows = [data]
        else:
            raise ValueError(f"Cannot convert data of type {type(data)} to CSV")
        
        if not rows:
            return ""
        
        # Get all unique keys from all dicts
        fieldnames = set()
        for row in rows:
            if isinstance(row, dict):
                fieldnames.update(row.keys())
        
        fieldnames = sorted(list(fieldnames))
        
        # Write CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        csv_str = output.getvalue()
        
        # Optionally write to file
        if output_file:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                f.write(csv_str)
        
        return csv_str
    
    @staticmethod
    def to_dataframe(result: Dict[str, Any]):
        """Export to pandas DataFrame.
        
        Args:
            result: Result dict from fetch_data()
        
        Returns:
            pandas DataFrame
        
        Requires:
            pandas (install with: pip install pandas)
        
        Example:
            client = HorizonsClient()
            result = client.fetch_data(config)
            df = DataExporter.to_dataframe(result)
            print(df.head())
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for DataFrame export. Install with: pip install pandas")
        
        if not result.get('success'):
            raise ValueError(f"Cannot export failed result: {result.get('error')}")
        
        data = result.get('data', {})
        
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame([data])
        else:
            raise ValueError(f"Cannot convert data of type {type(data)} to DataFrame")
    
    @staticmethod
    def to_astropy_table(result: Dict[str, Any]):
        """Export to Astropy Table.
        
        Args:
            result: Result dict from fetch_data()
        
        Returns:
            astropy.table.Table
        
        Requires:
            astropy (install with: pip install astropy)
        
        Example:
            client = HorizonsClient()
            result = client.fetch_data(config)
            table = DataExporter.to_astropy_table(result)
            print(table)
        """
        try:
            from astropy.table import Table
        except ImportError:
            raise ImportError("astropy is required for Table export. Install with: pip install astropy")
        
        if not result.get('success'):
            raise ValueError(f"Cannot export failed result: {result.get('error')}")
        
        data = result.get('data', {})
        
        # Convert to DataFrame first, then to Table
        df = DataExporter.to_dataframe(result)
        return Table.from_pandas(df)
    
    @staticmethod
    def save_json(result: Dict[str, Any], filepath: str, indent: int = 2) -> None:
        """Save result to JSON file.
        
        Args:
            result: Result dict from fetch_data()
            filepath: Output file path
            indent: JSON indentation
        
        Example:
            client = HorizonsClient()
            result = client.fetch_data(config)
            DataExporter.save_json(result, 'data.json')
        """
        json_str = DataExporter.to_json(result, indent=indent)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_str)
    
    @staticmethod
    def save_csv(result: Dict[str, Any], filepath: str) -> None:
        """Save result to CSV file.
        
        Args:
            result: Result dict from fetch_data()
            filepath: Output file path
        
        Example:
            client = HorizonsClient()
            result = client.fetch_data(config)
            DataExporter.save_csv(result, 'data.csv')
        """
        DataExporter.to_csv(result, output_file=filepath)
