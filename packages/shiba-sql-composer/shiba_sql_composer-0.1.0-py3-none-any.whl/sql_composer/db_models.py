from dataclasses import dataclass
from typing import List
from abc import ABC
from enum import Enum


@dataclass
class Column:
    name: str
    type_: Enum


class Table(ABC):
    name: str
    columns: List[Column] = []

    def __init__(self, name: str):
        self.name = name
        self.columns = [value for name, value in vars(self.__class__).items() if isinstance(value, Column)]
