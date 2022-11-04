from typing import List, Tuple

from asyncpg import Connection

from src.data_types import Value, ValueUnsaved, Post
from src.data_types import Comment, Like, Favorite
from src.search.elastic_searcher import ElasticSearcher


class Searcher:

    @classmethod
    def add_record(cls, topic: str = None, value: Value = None) -> None:
        post = Post(topic=topic, values=[value])
        ElasticSearcher.add_record(post=post)

    @classmethod
    def append_comment_by_topic_id(cls, topic_id: str = None, value: ValueUnsaved = None) -> None:
        ElasticSearcher.append_comment_by_id(id_=topic_id, value=value)

    @classmethod
    def get_relevant_topics(cls, message: str) -> List[Tuple[str, str]]:
        return ElasticSearcher.get_relevant_topics(message=message)

    @classmethod
    async def get_comments_by_topic_id(cls, topic_id: str, user_id: int, pool: Connection) -> List[Comment]:
        comments = []
        values = ElasticSearcher.get_comments_by_topic_id(id_=topic_id)
        for value in values:
            like = await Like.get(user_id=user_id, comment_id=value.get_id(), pool=pool)
            favorite = await Favorite.get(user_id=user_id, comment_id=value.get_id(), pool=pool)
            comments.append(Comment(value, like, favorite, topic_id))
        return sorted(comments)

    @classmethod
    def get_topic_by_id(cls, topic_id: str) -> str:
        return ElasticSearcher.get_topic_by_id(id_=topic_id)

    @classmethod
    async def get_comment_by_id(cls, comment_id: str, user_id: int, pool: Connection) -> Comment:
        value = ElasticSearcher.get_comment_by_id(id_=comment_id)
        like = await Like.get(user_id=user_id, comment_id=value.get_id(), pool=pool)
        favorite = await Favorite.get(user_id=user_id, comment_id=value.get_id(), pool=pool)
        return Comment(value, like, favorite)

    @classmethod
    def get_next_comment(cls, comment_id: str) -> Comment:
        pass
