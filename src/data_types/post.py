from typing import List

from src.data_types.values import Value


class Post:

    def __init__(self, topic: str = None, values: List[Value] = []):
        self.values = values
        self.topic = topic

    def set_topic(self, topic: str) -> None:
        self.topic = topic

    def append_value(self, key: Value) -> None:
        self.values.append(key)

    def get_topic(self) -> str:
        return self.topic

    def get_values(self) -> List[Value]:
        return self.values

    def get_id(self) -> str:
        return self.id
