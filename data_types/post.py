from data_types.values import Value


class Post:

    def __init__(self, key: str = None, values: list[Value] = []):
        self.values = values
        self.key = key

    def set_key(self, key: str) -> str:
        self.key = key

    def append_value(self, key: Value) -> None:
        self.values.append(key)

    def get_key(self) -> str:
        return self.key

    def get_values(self) -> list[Value]:
        return self.values

    def get_id(self) -> str:
        return self.id
