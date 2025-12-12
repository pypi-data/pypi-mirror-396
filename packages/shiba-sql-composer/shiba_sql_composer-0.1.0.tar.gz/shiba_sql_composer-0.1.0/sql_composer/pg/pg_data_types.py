from enum import Enum


class PgDataTypes(Enum):
    # String types
    TEXT = "text"
    VARCHAR = "varchar"
    CHAR = "char"
    CHARACTER_VARYING = "character varying"

    # Integer types
    INT = "int"
    INT4 = "int4"
    INTEGER = "integer"
    BIGINT = "bigint"
    INT8 = "int8"
    SMALLINT = "smallint"
    INT2 = "int2"

    # Numeric types
    NUMERIC = "numeric"
    DECIMAL = "decimal"
    REAL = "real"
    FLOAT4 = "float4"
    DOUBLE_PRECISION = "double precision"
    FLOAT8 = "float8"

    # Boolean types
    BOOLEAN = "boolean"
    BOOL = "bool"

    # Date/Time types
    DATE = "date"
    TIMESTAMP = "timestamp"
    TIMESTAMP_WITHOUT_TIME_ZONE = "timestamp without time zone"
    TIMESTAMPTZ = "timestamptz"
    TIMESTAMP_WITH_TIME_ZONE = "timestamp with time zone"
    TIME = "time"

    # JSON types
    JSON = "json"
    JSONB = "jsonb"

    # UUID type
    UUID = "uuid"
