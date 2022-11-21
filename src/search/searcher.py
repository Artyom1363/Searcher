from typing import List, Tuple

from asyncpg import Connection

from src.data_types import Value, ValueUnsaved, Post
from src.data_types import Comment, Like, Favorite
from src.search.elastic_searcher import ElasticSearcher


class Searcher:

    @classmethod
    async def add_record(cls, topic: str,
                         value: Value,
                         user_id: int,
                         pool: Connection) -> None:
        post = Post(topic=topic, values=[value])
        meta_info = ElasticSearcher.add_record(post=post)
        assert (len(meta_info) == 2)
        assert (len(meta_info[1]) == 1)
        query = f"" \
                f"INSERT INTO comments " \
                f"(author_id, comment_id, topic_id) VALUES " \
                f"('{user_id}', '{meta_info[1][0]}', '{meta_info[0]}')"

        await pool.fetch(query)

    @classmethod
    async def append_comment_by_topic_id(cls, topic_id: str,
                                         value: ValueUnsaved,
                                         user_id: int,
                                         pool: Connection) -> None:
        comment_id = ElasticSearcher.append_comment_by_id(id_=topic_id,
                                                          value=value)
        # print(f"{comment_id=} in append_comment_by_topic_id")
        query = f"" \
                f"INSERT INTO comments " \
                f"(author_id, comment_id, topic_id) VALUES " \
                f"('{user_id}', '{comment_id}', '{topic_id}')"

        await pool.fetch(query)

    @classmethod
    def get_relevant_topics(cls, message: str) -> List[Tuple[str, str]]:
        return ElasticSearcher.get_relevant_topics(message=message)

    @classmethod
    async def get_best_comment_by_topic_id(cls, topic_id: str,
                                           user_id: int,
                                           pool: Connection) -> Comment:
        order_query = "ORDER BY cnt DESC, MIN_ID"

        sub_query_1 = f"" \
                      f"  SELECT  " \
                      f"    MIN(id) as MIN_id, " \
                      f"      COUNT(*) AS cnt, " \
                      f"      comment_id, " \
                      f"      topic_id " \
                      f"      FROM (" \
                      f"        SELECT comments.id AS id," \
                      f"          comments.comment_id AS comment_id, " \
                      f"          topic_id " \
                      f"        FROM likes " \
                      f"        LEFT JOIN comments " \
                      f"        ON likes.comment_id = comments.comment_id" \
                      f"      ) AS full_likes_info " \
                      f"  WHERE topic_id = '{topic_id}' " \
                      f"  GROUP BY comment_id, topic_id " \
                      f"  {order_query} " \
                      f"  LIMIT 1 "

        sub_query_2 = f"" \
                      f"SELECT * FROM ({sub_query_1}) AS sub_1 " \
                      f"UNION " \
                      f"SELECT id AS MIN_id," \
                      f"  0 AS cnt," \
                      f"  comment_id," \
                      f"  topic_id" \
                      f"  FROM comments" \
                      f"  WHERE topic_id = '{topic_id}' AND " \
                      f"    comment_id NOT IN (" \
                      f"    SELECT comment_id" \
                      f"    FROM likes" \
                      f"  )" \


        sub_query_3 = f"" \
                      f"SELECT * FROM ( {sub_query_2} " \
                      f") AS suq_query_3 " \
                      f"{order_query} " \
                      f"LIMIT 1"

        query = f"" \
                f"SELECT comment_id FROM ( {sub_query_3} " \
                f") AS best"

        result = await pool.fetch(query)

        if result:
            comment_id = result[0][0]
            comment = await cls.get_comment_by_id(comment_id=comment_id,
                                                  user_id=user_id, pool=pool)
            return comment

    @classmethod
    def get_topic_by_id(cls, topic_id: str) -> str:
        return ElasticSearcher.get_topic_by_id(id_=topic_id)

    @classmethod
    async def get_comment_by_id(cls, comment_id: str,
                                user_id: int,
                                pool: Connection) -> Comment:
        value = ElasticSearcher.get_comment_by_id(id_=comment_id)
        like = await Like.get(user_id=user_id,
                              comment_id=value.get_id(),
                              pool=pool)
        favorite = await Favorite.get(user_id=user_id,
                                      comment_id=value.get_id(),
                                      pool=pool)
        return Comment(value, like, favorite)

    @classmethod
    async def get_next_comment(cls, comment_id: str,
                               user_id: int,
                               pool: Connection) -> Comment:
        query = cls.__get_iterate_comment_query(comment_id=comment_id,
                                                order_sign='>')

        result = await pool.fetch(query)

        if result:
            comment_id = result[0][1]
            comment = await cls.get_comment_by_id(comment_id=comment_id,
                                                  user_id=user_id, pool=pool)
            return comment

    @classmethod
    async def get_prev_comment(cls, comment_id: str,
                               user_id: int,
                               pool: Connection) -> Comment:
        query = cls.__get_iterate_comment_query(comment_id=comment_id,
                                                order_sign='<')

        result = await pool.fetch(query)

        if result:
            comment_id = result[0][1]
            comment = await cls.get_comment_by_id(comment_id=comment_id,
                                                  user_id=user_id,
                                                  pool=pool)
            return comment

    @classmethod
    def __get_iterate_comment_query(cls, comment_id: str,
                                    order_sign: str) -> str:
        if order_sign not in ('>', '<'):
            raise Exception("Wrong order_type in __get_iterate_comment_query "
                            "(must by '>' or '<') ")
        if order_sign == '>':
            order_type = 'ASC'
        else:
            order_type = 'DESC'

        order_query = "ORDER BY cnt DESC, MIN_ID"

        sub_query_1 = f"" \
            f"  SELECT  " \
            f"    MIN(id) as MIN_id, " \
            f"      COUNT(*) AS cnt, " \
            f"      comment_id, " \
            f"      topic_id " \
            f"      FROM (" \
            f"        SELECT comments.id AS id," \
            f"          comments.comment_id AS comment_id, " \
            f"          topic_id " \
            f"        FROM likes " \
            f"        LEFT JOIN comments " \
            f"        ON likes.comment_id = comments.comment_id" \
            f"      ) AS full_likes_info " \
            f"  GROUP BY comment_id, topic_id " \
            f"  {order_query} " \

        sub_query_2 = f"" \
            f"SELECT * FROM ({sub_query_1}) AS sub_1 " \
            f"UNION " \
            f"SELECT id AS MIN_id," \
            f"  0 AS cnt," \
            f"  comment_id," \
            f"  topic_id" \
            f"  FROM comments" \
            f"  WHERE " \
            f"    comment_id NOT IN (" \
            f"    SELECT comment_id" \
            f"    FROM likes" \
            f"  )"

        sub_query_3 = f"" \
            f"SELECT * FROM ( {sub_query_2} " \
            f") AS suq_query_3 " \
            f"{order_query} "

        sub_query_4 = f"" \
            f"SELECT ROW_NUMBER () OVER () as row_num, " \
            f"  MIN_id, cnt, " \
            f"  comment_id, topic_id " \
            f"  FROM ( " \
            f" {sub_query_3}" \
            f") AS ordered"

        query = f"" \
                f"SELECT row_num, comment_id, topic_id FROM ({sub_query_4}" \
                f") AS ordered " \
                f"WHERE row_num {order_sign} ( " \
                f"  SELECT row_num FROM ({sub_query_4} " \
                f"  ) AS pers_row_num" \
                f"  WHERE comment_id = '{comment_id}'" \
                f") " \
                f"AND topic_id = ( " \
                f"  SELECT topic_id " \
                f"  FROM comments " \
                f"  WHERE comment_id='{comment_id}' " \
                f"  LIMIT 1 " \
                f") " \
                f"ORDER BY row_num {order_type} " \
                f"LIMIT 1;"
        return query
