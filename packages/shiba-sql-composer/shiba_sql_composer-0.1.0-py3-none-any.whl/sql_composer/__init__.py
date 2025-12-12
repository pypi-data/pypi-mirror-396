"""
sql-composer: A type-safe SQL query builder and composer for Python.
"""

from sql_composer.sql_composer import SqlComposer
from sql_composer.sql_translator import SqlTranslator
from sql_composer.db_models import Table, Column
from sql_composer.db_conditions import (
    FilterOp,
    Where,
    WhereClause,
    Sort,
    SortType,
    Page,
    SqlQueryCriteria,
)

__version__ = "0.1.0"

__all__ = [
    # Core
    "SqlComposer",
    "SqlTranslator",
    # Models
    "Table",
    "Column",
    # Conditions
    "FilterOp",
    "Where",
    "WhereClause",
    "Sort",
    "SortType",
    "Page",
    "SqlQueryCriteria",
]
