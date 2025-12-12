from abc import ABC, abstractmethod
from typing import Any, List, Tuple
from sql_composer.db_models import Column, Table
from sql_composer.db_conditions import Where, Sort, Page, SqlQueryCriteria


class SqlTranslator(ABC):
    @abstractmethod
    def val_to_sql(self, column: Column, value: Any) -> str:
        pass

    @abstractmethod
    def where_to_sql(self, where: Where, column: Column) -> str:
        pass

    @abstractmethod
    def sort_to_sql(self, sort: Sort) -> str:
        pass

    @abstractmethod
    def page_criteria_to_sql(self, pagination: Page) -> str:
        pass

    @abstractmethod
    def query_criteria_to_sql(self, query_criteria: SqlQueryCriteria | None, table: Table) -> str:
        pass

    @abstractmethod
    def query_criteria_to_sql_with_params(
        self, query_criteria: SqlQueryCriteria | None, table: Table
    ) -> Tuple[str, List[Any]]:
        pass
