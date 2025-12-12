from dataclasses import dataclass
from typing import Optional


@dataclass
class PostgresColumnMetadata:
    """Represents metadata for a PostgreSQL column from information_schema.columns"""

    table_catalog: str
    table_schema: str
    table_name: str
    column_name: str
    ordinal_position: int
    column_default: Optional[str]
    is_nullable: str
    data_type: str
    character_maximum_length: Optional[int]
    character_octet_length: Optional[int]
    numeric_precision: Optional[int]
    numeric_precision_radix: Optional[int]
    numeric_scale: Optional[int]
    datetime_precision: Optional[int]
    interval_type: Optional[str]
    interval_precision: Optional[int]
    character_set_catalog: Optional[str]
    character_set_schema: Optional[str]
    character_set_name: Optional[str]
    collation_catalog: Optional[str]
    collation_schema: Optional[str]
    collation_name: Optional[str]
    domain_catalog: Optional[str]
    domain_schema: Optional[str]
    domain_name: Optional[str]
    udt_catalog: str
    udt_schema: str
    udt_name: str
    scope_catalog: Optional[str]
    scope_schema: Optional[str]
    scope_name: Optional[str]
    maximum_cardinality: Optional[int]
    dtd_identifier: str
    is_self_referencing: str
    is_identity: str
    identity_generation: Optional[str]
    identity_start: Optional[str]
    identity_increment: Optional[str]
    identity_maximum: Optional[str]
    identity_minimum: Optional[str]
    identity_cycle: str
    is_generated: str
    generation_expression: Optional[str]
    is_updatable: str

    @classmethod
    def from_dict(cls, data: dict) -> "PostgresColumnMetadata":
        """Create a PostgresColumnMetadata instance from a dictionary."""
        # Filter out duplicate keys and convert types appropriately
        filtered_data = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**filtered_data)
