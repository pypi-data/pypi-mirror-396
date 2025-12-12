import json
import math
from typing import Any, List, Tuple
from sql_composer.db_models import Column, Table
from sql_composer.db_conditions import Where, Sort, Page, SqlQueryCriteria
from sql_composer.pg.pg_data_types import PgDataTypes
from sql_composer.pg.pg_filter_op import PgFilterOp
from sql_composer.sql_translator import SqlTranslator


class PgSqlTranslator(SqlTranslator):
    """PostgreSQL Translator"""

    @staticmethod
    def _escape_string(value: str) -> str:
        """Enhanced string escaping for PostgreSQL - WARNING: Not sufficient for production use"""
        # Escape single quotes (PostgreSQL standard)
        value = value.replace("'", "''")
        # Escape backslashes (PostgreSQL specific)
        value = value.replace("\\", "\\\\")
        return value

    @staticmethod
    def _float_to_sql(value: float) -> str:
        """Convert a float value to PostgreSQL SQL representation.

        Handles special float values (infinity, -infinity, NaN) by returning
        the PostgreSQL-expected quoted string literals.
        """
        if isinstance(value, float):
            if math.isinf(value):
                return "'Infinity'" if value > 0 else "'-Infinity'"
            if math.isnan(value):
                return "'NaN'"
        return str(value)

    def val_to_sql(self, column: Column, value: Any) -> str:
        match column.type_:
            case PgDataTypes.TEXT | PgDataTypes.VARCHAR | PgDataTypes.CHAR | PgDataTypes.CHARACTER_VARYING:
                return f"'{self._escape_string(str(value))}'"
            case PgDataTypes.INT | PgDataTypes.INT4 | PgDataTypes.INTEGER:
                return str(value)
            case PgDataTypes.BIGINT | PgDataTypes.INT8:
                return str(value)
            case PgDataTypes.SMALLINT | PgDataTypes.INT2:
                return str(value)
            case PgDataTypes.NUMERIC | PgDataTypes.DECIMAL:
                return self._float_to_sql(value) if isinstance(value, float) else str(value)
            case PgDataTypes.REAL | PgDataTypes.FLOAT4:
                return self._float_to_sql(value) if isinstance(value, float) else str(value)
            case PgDataTypes.DOUBLE_PRECISION | PgDataTypes.FLOAT8:
                return self._float_to_sql(value) if isinstance(value, float) else str(value)
            case PgDataTypes.BOOLEAN | PgDataTypes.BOOL:
                return str(value).lower()
            case PgDataTypes.DATE:
                return f"'{self._escape_string(str(value))}'"
            case PgDataTypes.TIMESTAMP | PgDataTypes.TIMESTAMP_WITHOUT_TIME_ZONE:
                return f"'{self._escape_string(str(value))}'"
            case PgDataTypes.TIMESTAMPTZ | PgDataTypes.TIMESTAMP_WITH_TIME_ZONE:
                return f"'{self._escape_string(str(value))}'"
            case PgDataTypes.TIME:
                return f"'{self._escape_string(str(value))}'"
            case PgDataTypes.JSON | PgDataTypes.JSONB:
                # If value is already a string, validate it's valid JSON
                if isinstance(value, str):
                    try:
                        json.loads(value)
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Invalid JSON string for column '{column.name}': {e}")
                    return f"'{self._escape_string(value)}'"
                return f"'{self._escape_string(json.dumps(value))}'"
            case PgDataTypes.UUID:
                return f"'{self._escape_string(str(value))}'"
            case _:
                # Default case: treat as string
                return f"'{self._escape_string(str(value))}'"

    def where_to_sql(self, where: Where, column: Column) -> str:
        # Convert all values to SQL expressions
        values_as_pg_sql = [self.val_to_sql(column, value) for value in where.values]

        if len(values_as_pg_sql) != 1 and where.op in (
            PgFilterOp.EQUAL,
            PgFilterOp.NOT_EQUAL,
            PgFilterOp.LESS_THAN,
            PgFilterOp.LESS_THAN_OR_EQUAL,
            PgFilterOp.GREATER_THAN,
            PgFilterOp.GREATER_THAN_OR_EQUAL,
            PgFilterOp.LIKE,
            PgFilterOp.NOT_LIKE,
            PgFilterOp.ILIKE,
            PgFilterOp.NOT_ILIKE,
            PgFilterOp.REGEXP,
            PgFilterOp.NOT_REGEXP,
            PgFilterOp.REGEXP_CASE_INSENSITIVE,
            PgFilterOp.NOT_REGEXP_CASE_INSENSITIVE,
            PgFilterOp.CONTAINS,
            PgFilterOp.IS_CONTAINED_BY,
            PgFilterOp.OVERLAPS,
            PgFilterOp.JSON_CONTAINS,
            PgFilterOp.JSON_IS_CONTAINED_BY,
            PgFilterOp.JSON_HAS_KEY,
            PgFilterOp.JSON_HAS_ANY_KEY,
            PgFilterOp.JSON_HAS_ALL_KEYS,
            PgFilterOp.CONTAINS_STRING,
            PgFilterOp.NOT_CONTAINS_STRING,
            PgFilterOp.CONTAINS_STRING_CASE_INSENSITIVE,
            PgFilterOp.NOT_CONTAINS_STRING_CASE_INSENSITIVE,
            PgFilterOp.SIMILAR_TO,
            PgFilterOp.NOT_SIMILAR_TO,
            PgFilterOp.OVERLAPS_GEOMETRY,
            PgFilterOp.CONTAINS_GEOMETRY,
            PgFilterOp.IS_CONTAINED_BY_GEOMETRY,
            PgFilterOp.INTERSECTS,
            PgFilterOp.CONTAINS_INET,
            PgFilterOp.IS_CONTAINED_BY_INET,
            PgFilterOp.IS_SUBNET,
            PgFilterOp.IS_SUPERNET,
            PgFilterOp.FULLTEXT_MATCH,
            PgFilterOp.FULLTEXT_QUERY,
            PgFilterOp.IS_DISTINCT_FROM,
            PgFilterOp.IS_NOT_DISTINCT_FROM,
            PgFilterOp.ANY,
            PgFilterOp.ALL,
            PgFilterOp.SOME,
            PgFilterOp.EXISTS,
            PgFilterOp.NOT_EXISTS,
        ):
            raise ValueError(f"Operator {where.op} requires exactly 1 value, got {len(where.values)}")

        if len(values_as_pg_sql) != 2 and where.op in (
            PgFilterOp.BETWEEN,
            PgFilterOp.NOT_BETWEEN,
        ):
            raise ValueError(f"Operator {where.op} requires exactly 2 values, got {len(where.values)}")

        match where.op:
            # Single value operators - raise exception if multiple values provided
            case PgFilterOp.EQUAL:
                return f"{where.field} = {values_as_pg_sql[0]}"
            case PgFilterOp.NOT_EQUAL:
                return f"{where.field} != {values_as_pg_sql[0]}"
            case PgFilterOp.LESS_THAN:
                return f"{where.field} < {values_as_pg_sql[0]}"
            case PgFilterOp.LESS_THAN_OR_EQUAL:
                return f"{where.field} <= {values_as_pg_sql[0]}"
            case PgFilterOp.GREATER_THAN:
                return f"{where.field} > {values_as_pg_sql[0]}"
            case PgFilterOp.GREATER_THAN_OR_EQUAL:
                return f"{where.field} >= {values_as_pg_sql[0]}"

            # Multiple value operators - support multiple values
            case PgFilterOp.IN:
                if len(where.values) == 0:
                    raise ValueError(f"Operator {where.op} requires at least 1 value, got 0")
                if len(where.values) == 1:
                    return f"{where.field} = {values_as_pg_sql[0]}"
                else:
                    return f"{where.field} IN ({', '.join(values_as_pg_sql)})"
            case PgFilterOp.NOT_IN:
                if len(where.values) == 0:
                    raise ValueError(f"Operator {where.op} requires at least 1 value, got 0")
                if len(where.values) == 1:
                    return f"{where.field} != {values_as_pg_sql[0]}"
                else:
                    return f"{where.field} NOT IN ({', '.join(values_as_pg_sql)})"

            # No value operators
            case PgFilterOp.IS_NULL:
                return f"{where.field} IS NULL"
            case PgFilterOp.IS_NOT_NULL:
                return f"{where.field} IS NOT NULL"

            # Single value operators - pattern matching
            case PgFilterOp.LIKE:
                return f"{where.field} LIKE {values_as_pg_sql[0]}"
            case PgFilterOp.NOT_LIKE:
                return f"{where.field} NOT LIKE {values_as_pg_sql[0]}"
            case PgFilterOp.ILIKE:
                return f"{where.field} ILIKE {values_as_pg_sql[0]}"
            case PgFilterOp.NOT_ILIKE:
                return f"{where.field} NOT ILIKE {values_as_pg_sql[0]}"

            # Two value operators - range operators
            case PgFilterOp.BETWEEN:
                return f"{where.field} BETWEEN {values_as_pg_sql[0]} AND {values_as_pg_sql[1]}"
            case PgFilterOp.NOT_BETWEEN:
                return f"{where.field} NOT BETWEEN {values_as_pg_sql[0]} AND {values_as_pg_sql[1]}"

            # Single value operators - regular expressions
            case PgFilterOp.REGEXP:
                return f"{where.field} ~ {values_as_pg_sql[0]}"
            case PgFilterOp.NOT_REGEXP:
                return f"{where.field} !~ {values_as_pg_sql[0]}"
            case PgFilterOp.REGEXP_CASE_INSENSITIVE:
                return f"{where.field} ~* {values_as_pg_sql[0]}"
            case PgFilterOp.NOT_REGEXP_CASE_INSENSITIVE:
                return f"{where.field} !~* {values_as_pg_sql[0]}"

            # Single value operators - arrays
            case PgFilterOp.CONTAINS:
                return f"{where.field} @> {values_as_pg_sql[0]}"
            case PgFilterOp.IS_CONTAINED_BY:
                return f"{where.field} <@ {values_as_pg_sql[0]}"
            case PgFilterOp.OVERLAPS:
                return f"{where.field} && {values_as_pg_sql[0]}"

            # Single value operators - JSON
            case PgFilterOp.JSON_CONTAINS:
                return f"{where.field} @> {values_as_pg_sql[0]}"
            case PgFilterOp.JSON_IS_CONTAINED_BY:
                return f"{where.field} <@ {values_as_pg_sql[0]}"
            case PgFilterOp.JSON_HAS_KEY:
                return f"{where.field} ? {values_as_pg_sql[0]}"
            case PgFilterOp.JSON_HAS_ANY_KEY:
                return f"{where.field} ?| {values_as_pg_sql[0]}"
            case PgFilterOp.JSON_HAS_ALL_KEYS:
                return f"{where.field} ?& {values_as_pg_sql[0]}"

            # Single value operators - strings
            case PgFilterOp.CONTAINS_STRING:
                return f"{where.field} ~~ {values_as_pg_sql[0]}"
            case PgFilterOp.NOT_CONTAINS_STRING:
                return f"{where.field} !~~ {values_as_pg_sql[0]}"
            case PgFilterOp.CONTAINS_STRING_CASE_INSENSITIVE:
                return f"{where.field} ~~* {values_as_pg_sql[0]}"
            case PgFilterOp.NOT_CONTAINS_STRING_CASE_INSENSITIVE:
                return f"{where.field} !~~* {values_as_pg_sql[0]}"

            # Single value operators - similar to
            case PgFilterOp.SIMILAR_TO:
                return f"{where.field} SIMILAR TO {values_as_pg_sql[0]}"
            case PgFilterOp.NOT_SIMILAR_TO:
                return f"{where.field} NOT SIMILAR TO {values_as_pg_sql[0]}"

            # Single value operators - geometric
            case PgFilterOp.OVERLAPS_GEOMETRY:
                return f"{where.field} && {values_as_pg_sql[0]}"
            case PgFilterOp.CONTAINS_GEOMETRY:
                return f"{where.field} @> {values_as_pg_sql[0]}"
            case PgFilterOp.IS_CONTAINED_BY_GEOMETRY:
                return f"{where.field} <@ {values_as_pg_sql[0]}"
            case PgFilterOp.INTERSECTS:
                return f"{where.field} && {values_as_pg_sql[0]}"

            # Single value operators - network
            case PgFilterOp.CONTAINS_INET:
                return f"{where.field} >> {values_as_pg_sql[0]}"
            case PgFilterOp.IS_CONTAINED_BY_INET:
                return f"{where.field} << {values_as_pg_sql[0]}"
            case PgFilterOp.IS_SUBNET:
                return f"{where.field} >>= {values_as_pg_sql[0]}"
            case PgFilterOp.IS_SUPERNET:
                return f"{where.field} <<= {values_as_pg_sql[0]}"

            # Single value operators - full text search
            case PgFilterOp.FULLTEXT_MATCH:
                return f"{where.field} @@ {values_as_pg_sql[0]}"
            case PgFilterOp.FULLTEXT_QUERY:
                return f"{where.field} @@@ {values_as_pg_sql[0]}"

            # Single value operators - special comparison
            case PgFilterOp.IS_DISTINCT_FROM:
                return f"{where.field} IS DISTINCT FROM {values_as_pg_sql[0]}"
            case PgFilterOp.IS_NOT_DISTINCT_FROM:
                return f"{where.field} IS NOT DISTINCT FROM {values_as_pg_sql[0]}"

            # Single value operators - subquery
            case PgFilterOp.ANY:
                return f"{where.field} = ANY({values_as_pg_sql[0]})"
            case PgFilterOp.ALL:
                return f"{where.field} = ALL({values_as_pg_sql[0]})"
            case PgFilterOp.SOME:
                return f"{where.field} = SOME({values_as_pg_sql[0]})"

            # Single value operators - exists
            case PgFilterOp.EXISTS:
                return f"EXISTS({values_as_pg_sql[0]})"
            case PgFilterOp.NOT_EXISTS:
                return f"NOT EXISTS({values_as_pg_sql[0]})"

            # Default case for any unhandled operators
            case _:
                raise ValueError(f"Unsupported operator: {where.op} for field {where.field}")

    def sort_to_sql(self, sort: Sort) -> str:
        return f"{sort.field} {sort.sort_type.value}"

    def page_criteria_to_sql(self, pagination: Page) -> str:
        page_criteria_as_sql = []
        if pagination.limit:
            page_criteria_as_sql.append(f"LIMIT {pagination.limit}")
        if pagination.offset:
            page_criteria_as_sql.append(f"OFFSET {pagination.offset}")
        return " ".join(page_criteria_as_sql)

    def query_criteria_to_sql(self, query_criteria: SqlQueryCriteria | None, table: Table) -> str:
        query_criteria_as_sql = ""
        if query_criteria is None:
            return query_criteria_as_sql

        columns_by_name = {c.name: c for c in table.columns}

        # Query Criteria - Where
        if query_criteria.where:
            conditions_as_sql = [
                f"{self.where_to_sql(condition, columns_by_name[condition.field])}"
                for condition in query_criteria.where.conditions
                if condition.field in columns_by_name
            ]

            if conditions_as_sql:
                conditions_as_sql = "\nAND ".join(conditions_as_sql)
                query_criteria_as_sql += f"\nWHERE {conditions_as_sql}"

        # Query Criteria - Sort
        if query_criteria.sort:
            sort_criteria_as_sql = [
                f"{self.sort_to_sql(sort)}" for sort in query_criteria.sort if sort.field in columns_by_name
            ]

            if sort_criteria_as_sql:
                sort_criteria_as_sql = " ".join(sort_criteria_as_sql)
                query_criteria_as_sql += f"\nORDER BY {sort_criteria_as_sql}"

        # Query Criteria - Pagination
        if query_criteria.page:
            query_criteria_as_sql += f"\n{self.page_criteria_to_sql(query_criteria.page)}"

        return query_criteria_as_sql

    def query_criteria_to_sql_with_params(
        self, query_criteria: SqlQueryCriteria | None, table: Table
    ) -> Tuple[str, List[Any]]:
        """
        Generate parameterized SQL with extracted parameters.
        Returns a tuple of (SQL with %s placeholders, parameters list).
        """
        if query_criteria is None:
            return "", []

        columns_by_name = {c.name: c for c in table.columns}
        query_criteria_as_sql = ""
        params = []

        # Query Criteria - Where
        if query_criteria.where:
            conditions_as_sql = []
            for condition in query_criteria.where.conditions:
                if condition.field in columns_by_name:
                    condition_sql, condition_params = self.where_to_sql_with_params(condition)
                    conditions_as_sql.append(condition_sql)
                    params.extend(condition_params)

            if conditions_as_sql:
                conditions_as_sql = "\nAND ".join(conditions_as_sql)
                query_criteria_as_sql += f"\nWHERE {conditions_as_sql}"

        # Query Criteria - Sort
        if query_criteria.sort:
            sort_criteria_as_sql = [
                f"{self.sort_to_sql(sort)}" for sort in query_criteria.sort if sort.field in columns_by_name
            ]

            if sort_criteria_as_sql:
                sort_criteria_as_sql = " ".join(sort_criteria_as_sql)
                query_criteria_as_sql += f"\nORDER BY {sort_criteria_as_sql}"

        # Query Criteria - Pagination
        if query_criteria.page:
            query_criteria_as_sql += f"\n{self.page_criteria_to_sql(query_criteria.page)}"

        return query_criteria_as_sql, params

    def where_to_sql_with_params(self, where: Where) -> Tuple[str, List[Any]]:
        """
        Generate parameterized WHERE clause with extracted parameters.
        Returns a tuple of (SQL with %s placeholders, parameters list).
        """

        # Validate number of values for the operator
        if len(where.values) != 1 and where.op in (
            PgFilterOp.EQUAL,
            PgFilterOp.NOT_EQUAL,
            PgFilterOp.LESS_THAN,
            PgFilterOp.LESS_THAN_OR_EQUAL,
            PgFilterOp.GREATER_THAN,
            PgFilterOp.GREATER_THAN_OR_EQUAL,
            PgFilterOp.LIKE,
            PgFilterOp.NOT_LIKE,
            PgFilterOp.ILIKE,
            PgFilterOp.NOT_ILIKE,
            PgFilterOp.REGEXP,
            PgFilterOp.NOT_REGEXP,
            PgFilterOp.REGEXP_CASE_INSENSITIVE,
            PgFilterOp.NOT_REGEXP_CASE_INSENSITIVE,
            PgFilterOp.CONTAINS,
            PgFilterOp.IS_CONTAINED_BY,
            PgFilterOp.OVERLAPS,
            PgFilterOp.JSON_CONTAINS,
            PgFilterOp.JSON_IS_CONTAINED_BY,
            PgFilterOp.JSON_HAS_KEY,
            PgFilterOp.JSON_HAS_ANY_KEY,
            PgFilterOp.JSON_HAS_ALL_KEYS,
            PgFilterOp.CONTAINS_STRING,
            PgFilterOp.NOT_CONTAINS_STRING,
            PgFilterOp.CONTAINS_STRING_CASE_INSENSITIVE,
            PgFilterOp.NOT_CONTAINS_STRING_CASE_INSENSITIVE,
            PgFilterOp.SIMILAR_TO,
            PgFilterOp.NOT_SIMILAR_TO,
            PgFilterOp.OVERLAPS_GEOMETRY,
            PgFilterOp.CONTAINS_GEOMETRY,
            PgFilterOp.IS_CONTAINED_BY_GEOMETRY,
            PgFilterOp.INTERSECTS,
            PgFilterOp.CONTAINS_INET,
            PgFilterOp.IS_CONTAINED_BY_INET,
            PgFilterOp.IS_SUBNET,
            PgFilterOp.IS_SUPERNET,
            PgFilterOp.FULLTEXT_MATCH,
            PgFilterOp.FULLTEXT_QUERY,
            PgFilterOp.IS_DISTINCT_FROM,
            PgFilterOp.IS_NOT_DISTINCT_FROM,
            PgFilterOp.ANY,
            PgFilterOp.ALL,
            PgFilterOp.SOME,
            PgFilterOp.EXISTS,
            PgFilterOp.NOT_EXISTS,
        ):
            raise ValueError(f"Operator {where.op} requires exactly 1 value, got {len(where.values)}")

        if len(where.values) != 2 and where.op in (
            PgFilterOp.BETWEEN,
            PgFilterOp.NOT_BETWEEN,
        ):
            raise ValueError(f"Operator {where.op} requires exactly 2 values, got {len(where.values)}")

        # Handle operators that need parameters
        match where.op:
            # Single value operators
            case PgFilterOp.EQUAL:
                return f"{where.field} = %s", [where.values[0]]
            case PgFilterOp.NOT_EQUAL:
                return f"{where.field} != %s", [where.values[0]]
            case PgFilterOp.LESS_THAN:
                return f"{where.field} < %s", [where.values[0]]
            case PgFilterOp.LESS_THAN_OR_EQUAL:
                return f"{where.field} <= %s", [where.values[0]]
            case PgFilterOp.GREATER_THAN:
                return f"{where.field} > %s", [where.values[0]]
            case PgFilterOp.GREATER_THAN_OR_EQUAL:
                return f"{where.field} >= %s", [where.values[0]]

            case PgFilterOp.IS_NULL:
                return f"{where.field} IS NULL", []
            case PgFilterOp.IS_NOT_NULL:
                return f"{where.field} IS NOT NULL", []

            # Multiple value operators
            case PgFilterOp.IN:
                if len(where.values) == 0:
                    raise ValueError(f"Operator {where.op} requires at least 1 value, got 0")
                if len(where.values) == 1:
                    return f"{where.field} = %s", [where.values[0]]
                else:
                    placeholders = ", ".join(["%s"] * len(where.values))
                    return f"{where.field} IN ({placeholders})", where.values
            case PgFilterOp.NOT_IN:
                if len(where.values) == 0:
                    raise ValueError(f"Operator {where.op} requires at least 1 value, got 0")
                if len(where.values) == 1:
                    return f"{where.field} != %s", [where.values[0]]
                else:
                    placeholders = ", ".join(["%s"] * len(where.values))
                    return f"{where.field} NOT IN ({placeholders})", where.values

            # Pattern matching operators
            case PgFilterOp.LIKE:
                return f"{where.field} LIKE %s", [where.values[0]]
            case PgFilterOp.NOT_LIKE:
                return f"{where.field} NOT LIKE %s", [where.values[0]]
            case PgFilterOp.ILIKE:
                return f"{where.field} ILIKE %s", [where.values[0]]
            case PgFilterOp.NOT_ILIKE:
                return f"{where.field} NOT ILIKE %s", [where.values[0]]

            # Range operators
            case PgFilterOp.BETWEEN:
                return f"{where.field} BETWEEN %s AND %s", where.values
            case PgFilterOp.NOT_BETWEEN:
                return f"{where.field} NOT BETWEEN %s AND %s", where.values

            # Regular expressions
            case PgFilterOp.REGEXP:
                return f"{where.field} ~ %s", [where.values[0]]
            case PgFilterOp.NOT_REGEXP:
                return f"{where.field} !~ %s", [where.values[0]]
            case PgFilterOp.REGEXP_CASE_INSENSITIVE:
                return f"{where.field} ~* %s", [where.values[0]]
            case PgFilterOp.NOT_REGEXP_CASE_INSENSITIVE:
                return f"{where.field} !~* %s", [where.values[0]]

            # Array operators
            case PgFilterOp.CONTAINS:
                return f"{where.field} @> %s", [where.values[0]]
            case PgFilterOp.IS_CONTAINED_BY:
                return f"{where.field} <@ %s", [where.values[0]]
            case PgFilterOp.OVERLAPS:
                return f"{where.field} && %s", [where.values[0]]

            # JSON operators
            case PgFilterOp.JSON_CONTAINS:
                return f"{where.field} @> %s", [where.values[0]]
            case PgFilterOp.JSON_IS_CONTAINED_BY:
                return f"{where.field} <@ %s", [where.values[0]]
            case PgFilterOp.JSON_HAS_KEY:
                return f"{where.field} ? %s", [where.values[0]]
            case PgFilterOp.JSON_HAS_ANY_KEY:
                return f"{where.field} ?| %s", [where.values[0]]
            case PgFilterOp.JSON_HAS_ALL_KEYS:
                return f"{where.field} ?& %s", [where.values[0]]

            # String operators
            case PgFilterOp.CONTAINS_STRING:
                return f"{where.field} ~~ %s", [where.values[0]]
            case PgFilterOp.NOT_CONTAINS_STRING:
                return f"{where.field} !~~ %s", [where.values[0]]
            case PgFilterOp.CONTAINS_STRING_CASE_INSENSITIVE:
                return f"{where.field} ~~* %s", [where.values[0]]
            case PgFilterOp.NOT_CONTAINS_STRING_CASE_INSENSITIVE:
                return f"{where.field} !~~* %s", [where.values[0]]

            # Similar to
            case PgFilterOp.SIMILAR_TO:
                return f"{where.field} SIMILAR TO %s", [where.values[0]]
            case PgFilterOp.NOT_SIMILAR_TO:
                return f"{where.field} NOT SIMILAR TO %s", [where.values[0]]

            # Geometric operators
            case PgFilterOp.OVERLAPS_GEOMETRY:
                return f"{where.field} && %s", [where.values[0]]
            case PgFilterOp.CONTAINS_GEOMETRY:
                return f"{where.field} @> %s", [where.values[0]]
            case PgFilterOp.IS_CONTAINED_BY_GEOMETRY:
                return f"{where.field} <@ %s", [where.values[0]]
            case PgFilterOp.INTERSECTS:
                return f"{where.field} && %s", [where.values[0]]

            # Network operators
            case PgFilterOp.CONTAINS_INET:
                return f"{where.field} >> %s", [where.values[0]]
            case PgFilterOp.IS_CONTAINED_BY_INET:
                return f"{where.field} << %s", [where.values[0]]
            case PgFilterOp.IS_SUBNET:
                return f"{where.field} >>= %s", [where.values[0]]
            case PgFilterOp.IS_SUPERNET:
                return f"{where.field} <<= %s", [where.values[0]]

            # Full text search
            case PgFilterOp.FULLTEXT_MATCH:
                return f"{where.field} @@ %s", [where.values[0]]
            case PgFilterOp.FULLTEXT_QUERY:
                return f"{where.field} @@@ %s", [where.values[0]]

            # Special comparison
            case PgFilterOp.IS_DISTINCT_FROM:
                return f"{where.field} IS DISTINCT FROM %s", [where.values[0]]
            case PgFilterOp.IS_NOT_DISTINCT_FROM:
                return f"{where.field} IS NOT DISTINCT FROM %s", [where.values[0]]

            # Subquery operators
            case PgFilterOp.ANY:
                return f"{where.field} = ANY(%s)", [where.values[0]]
            case PgFilterOp.ALL:
                return f"{where.field} = ALL(%s)", [where.values[0]]
            case PgFilterOp.SOME:
                return f"{where.field} = SOME(%s)", [where.values[0]]

            # Exists operators
            case PgFilterOp.EXISTS:
                return "EXISTS(%s)", [where.values[0]]
            case PgFilterOp.NOT_EXISTS:
                return "NOT EXISTS(%s)", [where.values[0]]

            # Default case for any unhandled operators
            case _:
                raise ValueError(f"Unsupported operator: {where.op} for field {where.field}")
