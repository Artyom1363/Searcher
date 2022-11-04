from typing import List

from src.data_types.values import Value


class Post:

    def __init__(self, key: str = None, values: List[Value] = []):
        self.values = values
        self.key = key

    def set_key(self, key: str) -> str:
        self.key = key

    def append_value(self, key: Value) -> None:
        self.values.append(key)

    def get_key(self) -> str:
        return self.key

    def get_values(self) -> List[Value]:
        return self.values

    def get_id(self) -> str:
        return self.id
