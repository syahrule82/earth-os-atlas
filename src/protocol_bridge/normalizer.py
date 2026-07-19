"""Data normalizer — Schema mapping and data transformation."""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import time

@dataclass
class SchemaMapper:
    """Maps fields between external schemas and ATLAS schema."""
    mapping_name: str
    source_schema: Dict[str, str]  # external_field -> atlas_field
    transformations: Dict[str, str] = field(default_factory=dict)  # field -> transform function
    
    def map(self, external_data: dict) -> dict:
        """Map external data to ATLAS schema."""
        result = {}
        for ext_field, atlas_field in self.source_schema.items():
            if ext_field in external_data:
                value = external_data[ext_field]
                transform = self.transformations.get(ext_field)
                if transform == "to_decimal":
                    value = str(value)
                elif transform == "to_timestamp":
                    if isinstance(value, str):
                        value = time.time()  # Simplified
                elif transform == "to_did":
                    if not str(value).startswith("did:"):
                        value = f"did:atlas:{value}"
                result[atlas_field] = value
        return result
    
    def reverse_map(self, atlas_data: dict) -> dict:
        """Map ATLAS data back to external schema."""
        reverse = {v: k for k, v in self.source_schema.items()}
        return {reverse.get(k, k): v for k, v in atlas_data.items()}

class DataNormalizer:
    """
    Normalizes data from various external sources to a common ATLAS format.
    Handles unit conversion, date formatting, currency conversion, etc.
    """
    
    CURRENCY_RATES = {
        "USD": 1.0, "EUR": 0.85, "GBP": 0.73, "JPY": 110.0,
        "IDR": 14000.0, "CNY": 6.45, "INR": 73.0,
    }
    
    UNIT_CONVERSIONS = {
        "kg_to_g": 1000, "km_to_m": 1000,
        "hours_to_seconds": 3600, "days_to_seconds": 86400,
    }
    
    def __init__(self):
        self.mappers: Dict[str, SchemaMapper] = {}
    
    def register_mapper(self, mapper: SchemaMapper) -> None:
        self.mappers[mapper.mapping_name] = mapper
    
    def normalize(self, data: dict, source: str) -> dict:
        """Normalize data from a specific source."""
        mapper = self.mappers.get(source)
        if mapper:
            data = mapper.map(data)
        # Normalize timestamps to Unix
        for key in ["timestamp", "created_at", "updated_at"]:
            if key in data and isinstance(data[key], str):
                data[key] = time.time()  # Simplified parsing
        return data
    
    def convert_currency(self, amount: float, from_currency: str,
                        to_currency: str = "USD") -> float:
        """Convert amount between currencies."""
        from_rate = self.CURRENCY_RATES.get(from_currency, 1.0)
        to_rate = self.CURRENCY_RATES.get(to_currency, 1.0)
        return amount * (to_rate / from_rate)
    
    def convert_unit(self, value: float, conversion: str) -> float:
        """Convert units using predefined conversion factors."""
        factor = self.UNIT_CONVERSIONS.get(conversion, 1)
        return value * factor
    
    def normalize_address(self, address: str) -> str:
        """Normalize to DID:atlas format."""
        if not address.startswith("did:"):
            return f"did:atlas:{address}"
        return address
