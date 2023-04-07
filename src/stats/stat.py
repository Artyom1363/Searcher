from typing import List, Tuple

from asyncpg import Connection

from src.data_types import Comment

from src.search import Searcher



class Stat:
    @classmethod
    async def get(cls, user_id: int, pool: Connection):
        your_likes_query = f"" \
            f"SELECT COUNT(*) " \
            f"FROM likes " \
            f"WHERE comment_id " \
            f"IN ( " \
            f"  SELECT comment_id " \
            f"  FROM comments " \
            f"  WHERE author_id = {user_id} " \
            f")"

        your_likes = await pool.fetch(your_likes_query)
        your_likes_count = your_likes[0][0]

        favorites_count_query = f"" \
            f"SELECT COUNT(*) " \
            f"FROM favorites " \
            f"WHERE user_id = {user_id} "

        your_favorites = await pool.fetch(favorites_count_query)
        your_favorites_count = your_favorites[0][0]

        comments_count_query = f"" \
            f"SELECT COUNT(*) " \
            f"FROM comments " \
            f"WHERE author_id = {user_id} "

        your_comments = await pool.fetch(comments_count_query)
        your_comments_count = your_comments[0][0]

        stat = Stat(likes=your_likes_count,
                    favorites=your_favorites_count,
                    comments=your_comments_count)
        return stat

    def __init__(self, likes: int, favorites: int, comments: int):
        self.likes = likes
        self.favorites = favorites
        self.comments = comments

    @classmethod
    async def get_favorites_comments(cls, user_id: int, pool: Connection) -> List[Comment]:
        favorites_query = f"" \
            f"SELECT comment_id " \
            f"FROM favorites " \
            f"WHERE user_id = {user_id} "

        favorites = await pool.fetch(favorites_query)
        comments = []
        for favorite in favorites:
            comment = await Searcher.get_comment_by_id(comment_id=favorite[0],
                                                       user_id=user_id,
                                                       pool=pool)

            comments.append(comment)

        return comments
