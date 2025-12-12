from typing import List, Any
from enum import Enum
from dataclasses import dataclass


# Sort Clause
class SortType(Enum):
    ASC = "ASC"
    DESC = "DESC"


@dataclass
class Sort:
    field: str
    sort_type: SortType


# Pagination Clause
@dataclass
class Page:
    limit: int | None = None
    offset: int | None = None


# Filter Operators
@dataclass
class FilterOp:
    name: str
    sql: str


@dataclass
class Where:
    field: str
    op: FilterOp
    values: List[Any]


# WHERE Clause
@dataclass
class WhereClause:
    conditions: List[Where]


# SQL Query Criteria - Wrapper for all query conditions
@dataclass
class SqlQueryCriteria:
    where: WhereClause | None = None
    sort: List[Sort] | None = None
    page: Page | None = None
