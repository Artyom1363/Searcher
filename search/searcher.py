from data_types.values import Value
from data_types.post import Post


class Searcher:

    @classmethod
    def add_record(cls, post: Post = None):
        pass

    @classmethod
    def append_comment_by_id(cls, id_: str = None, value: Value = None):
        pass

    @classmethod
    def get_relevant(cls, message: str) -> list[Post]:
        pass
