from abc import abstractmethod


class Value:
    @abstractmethod
    def get_type(self) -> str:
        pass

    def get_info(self) -> dict:
        pass

    def get_id(self) -> str:
        pass


class Sentence(Value):
    def __init__(self, sentence: str = None, _id: str = None, _type: str = None, **kwargs) -> None:
        self.sentence = sentence
        self.id = _id
        self.type = _type

    def get_type(self) -> str:
        return 'Sentence'

    def get_info(self) -> dict:
        return {'sentence': self.sentence}

    def get_id(self) -> str:
        return self.id

    def get_sentence(self) -> str:
        return self.sentence
