from sql_composer.db_conditions import FilterOp


# TODO If sql is not needed, remove it and keep the name only
class PgFilterOp:
    # Comparison operators
    EQUAL = FilterOp(name="EQUAL", sql="=")
    NOT_EQUAL = FilterOp(name="NOT_EQUAL", sql="!=")
    LESS_THAN = FilterOp(name="LESS_THAN", sql="<")
    LESS_THAN_OR_EQUAL = FilterOp(name="LESS_THAN_OR_EQUAL", sql="<=")
    GREATER_THAN = FilterOp(name="GREATER_THAN", sql=">")
    GREATER_THAN_OR_EQUAL = FilterOp(name="GREATER_THAN_OR_EQUAL", sql=">=")

    # Pattern matching operators
    LIKE = FilterOp(name="LIKE", sql="LIKE")
    NOT_LIKE = FilterOp(name="NOT_LIKE", sql="NOT LIKE")
    ILIKE = FilterOp(name="ILIKE", sql="ILIKE")
    NOT_ILIKE = FilterOp(name="NOT_ILIKE", sql="NOT ILIKE")
    SIMILAR_TO = FilterOp(name="SIMILAR_TO", sql="SIMILAR TO")
    NOT_SIMILAR_TO = FilterOp(name="NOT_SIMILAR_TO", sql="NOT SIMILAR TO")
    REGEXP = FilterOp(name="REGEXP", sql="~")
    NOT_REGEXP = FilterOp(name="NOT_REGEXP", sql="!~")
    REGEXP_CASE_INSENSITIVE = FilterOp(name="REGEXP_CASE_INSENSITIVE", sql="~*")
    NOT_REGEXP_CASE_INSENSITIVE = FilterOp(name="NOT_REGEXP_CASE_INSENSITIVE", sql="!~*")

    # Set membership operators
    IN = FilterOp(name="IN", sql="IN")
    NOT_IN = FilterOp(name="NOT_IN", sql="NOT IN")

    # Null operators
    IS_NULL = FilterOp(name="IS_NULL", sql="IS NULL")
    IS_NOT_NULL = FilterOp(name="IS_NOT_NULL", sql="IS NOT NULL")

    # Range operators
    BETWEEN = FilterOp(name="BETWEEN", sql="BETWEEN")
    NOT_BETWEEN = FilterOp(name="NOT_BETWEEN", sql="NOT BETWEEN")

    # Array operators
    CONTAINS = FilterOp(name="CONTAINS", sql="@>")
    IS_CONTAINED_BY = FilterOp(name="IS_CONTAINED_BY", sql="<@")
    OVERLAPS = FilterOp(name="OVERLAPS", sql="&&")

    # JSON operators
    JSON_CONTAINS = FilterOp(name="JSON_CONTAINS", sql="@>")
    JSON_IS_CONTAINED_BY = FilterOp(name="JSON_IS_CONTAINED_BY", sql="<@")
    JSON_HAS_KEY = FilterOp(name="JSON_HAS_KEY", sql="?")
    JSON_HAS_ANY_KEY = FilterOp(name="JSON_HAS_ANY_KEY", sql="?|")
    JSON_HAS_ALL_KEYS = FilterOp(name="JSON_HAS_ALL_KEYS", sql="?&")

    # String operators
    CONTAINS_STRING = FilterOp(name="CONTAINS_STRING", sql="~~")
    NOT_CONTAINS_STRING = FilterOp(name="NOT_CONTAINS_STRING", sql="!~~")
    CONTAINS_STRING_CASE_INSENSITIVE = FilterOp(name="CONTAINS_STRING_CASE_INSENSITIVE", sql="~~*")
    NOT_CONTAINS_STRING_CASE_INSENSITIVE = FilterOp(name="NOT_CONTAINS_STRING_CASE_INSENSITIVE", sql="!~~*")

    # Geometric operators
    OVERLAPS_GEOMETRY = FilterOp(name="OVERLAPS_GEOMETRY", sql="&&")
    CONTAINS_GEOMETRY = FilterOp(name="CONTAINS_GEOMETRY", sql="@>")
    IS_CONTAINED_BY_GEOMETRY = FilterOp(name="IS_CONTAINED_BY_GEOMETRY", sql="<@")
    INTERSECTS = FilterOp(name="INTERSECTS", sql="&&")

    # Network operators
    CONTAINS_INET = FilterOp(name="CONTAINS_INET", sql=">>")
    IS_CONTAINED_BY_INET = FilterOp(name="IS_CONTAINED_BY_INET", sql="<<")
    IS_SUBNET = FilterOp(name="IS_SUBNET", sql=">>=")
    IS_SUPERNET = FilterOp(name="IS_SUPERNET", sql="<<=")

    # Full text search operators
    FULLTEXT_MATCH = FilterOp(name="FULLTEXT_MATCH", sql="@@")
    FULLTEXT_QUERY = FilterOp(name="FULLTEXT_QUERY", sql="@@@")

    # Special comparison operators
    IS_DISTINCT_FROM = FilterOp(name="IS_DISTINCT_FROM", sql="IS DISTINCT FROM")
    IS_NOT_DISTINCT_FROM = FilterOp(name="IS_NOT_DISTINCT_FROM", sql="IS NOT DISTINCT FROM")

    # Subquery operators
    ANY = FilterOp(name="ANY", sql="ANY")
    ALL = FilterOp(name="ALL", sql="ALL")
    SOME = FilterOp(name="SOME", sql="SOME")

    # Exists operators
    EXISTS = FilterOp(name="EXISTS", sql="EXISTS")
    NOT_EXISTS = FilterOp(name="NOT_EXISTS", sql="NOT EXISTS")
