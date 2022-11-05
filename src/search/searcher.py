from typing import List, Tuple

from asyncpg import Connection

from src.data_types import Value, ValueUnsaved, Post
from src.data_types import Comment, Like, Favorite
from src.search.elastic_searcher import ElasticSearcher


class Searcher:

    @classmethod
    async def add_record(cls, topic: str, value: Value, pool: Connection) -> None:
        post = Post(topic=topic, values=[value])
        meta_info = ElasticSearcher.add_record(post=post)
        assert (len(meta_info) == 2)
        assert (len(meta_info[1]) == 1)
        query = f"" \
            f"INSERT INTO likes " \
            f"(comment_id, topic_id) VALUES " \
            f"('{meta_info[0]}', '{meta_info[1][0]}')"

        await pool.fetch(query)

    @classmethod
    def append_comment_by_topic_id(cls, topic_id: str = None, value: ValueUnsaved = None) -> None:
        ElasticSearcher.append_comment_by_id(id_=topic_id, value=value)

    @classmethod
    def get_relevant_topics(cls, message: str) -> List[Tuple[str, str]]:
        return ElasticSearcher.get_relevant_topics(message=message)

    @classmethod
    async def get_comments_by_topic_id(cls, topic_id: str,
                                       user_id: int,
                                       pool: Connection,
                                       limit: int = None) -> List[Comment]:
        comments = []
        values = ElasticSearcher.get_comments_by_topic_id(id_=topic_id)
        for value in values:
            like = await Like.get(user_id=user_id,
                                  comment_id=value.get_id(),
                                  topic_id=value.get_topic_id(),
                                  pool=pool)
            favorite = await Favorite.get(user_id=user_id, comment_id=value.get_id(), pool=pool)
            comments.append(Comment(value, like, favorite))
        return sorted(comments)[0:limit]

    @classmethod
    def get_topic_by_id(cls, topic_id: str) -> str:
        return ElasticSearcher.get_topic_by_id(id_=topic_id)

    @classmethod
    async def get_comment_by_id(cls, comment_id: str, user_id: int, pool: Connection) -> Comment:
        value = ElasticSearcher.get_comment_by_id(id_=comment_id)
        like = await Like.get(user_id=user_id,
                              comment_id=value.get_id(),
                              topic_id=value.get_topic_id(),
                              pool=pool)
        favorite = await Favorite.get(user_id=user_id, comment_id=value.get_id(), pool=pool)
        return Comment(value, like, favorite)

    @classmethod
    async def get_next_comment(cls, comment_id: str, user_id: int, pool: Connection) -> Comment:
        query = f"" \
            f"SELECT cnt, comment_id, topic_id FROM (" \
            f"    SELECT COUNT(*) AS cnt, comment_id, topic_id" \
            f"    FROM likes " \
            f"    GROUP BY comment_id, topic_id" \
            f"    ORDER BY cnt DESC, " \
            f"    comment_id DESC " \
            f") AS ordered " \
            f"WHERE cnt < ( " \
            f"    SELECT COUNT(*) AS cnt2"  \
            f"    FROM likes " \
            f"    WHERE comment_id='{comment_id}'" \
            f")" \
            f"AND topic_id = (" \
            f"    SELECT topic_id " \
            f"    FROM likes" \
            f"    WHERE comment_id='{comment_id}'" \
            f"    LIMIT 1" \
            f")" \
            f"LIMIT 1;"

        # print(f"{query=}")
        result = await pool.fetch(query)

        if result:
            comment_id = result[0][1]
            comment = await cls.get_comment_by_id(comment_id=comment_id, user_id=user_id, pool=pool)
            # print(f"{result[0]=}")
            # print(f"{result[0][1]=}")
            return comment

    @classmethod
    def get_prev_comment(cls, comment_id: str, user_id: int, pool: Connection) -> Comment:
        pass
