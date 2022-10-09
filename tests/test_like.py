import unittest
from unittest import mock
from unittest.mock import AsyncMock
from src.likes import Like, LikeOn, LikeOff


class TestLikes(unittest.IsolatedAsyncioTestCase):
    async def test_creating_like_on(self):
        pool = AsyncMock()
        pool.fetch = AsyncMock(return_value=[[10, 1]])
        like = await Like.get(1, "comment_id", pool)
        like_on = LikeOn(1, "comment_id", 10, pool)
        self.assertEqual(like, Like(like_on))
        self.assertEqual(like.is_on(), True)
        self.assertEqual(like.get_total_likes(), 10)
        self.assertEqual(mock.call(f"SELECT"
                                   f"(SELECT COUNT(*) FROM likes WHERE comment_id = 'comment_id') AS total,"
                                   f"(SELECT COUNT(*) FROM likes WHERE user_id = 1 "
                                   f"and comment_id = 'comment_id' ) AS personal;"),
                         pool.fetch.mock_calls[0])

    async def test_creating_like_off(self):
        pool = AsyncMock()
        pool.fetch = AsyncMock(return_value=[[10, 0]])
        like = await Like.get(2, "id_comment", pool)
        like_off = LikeOff(2, "id_comment", 10, pool)
        self.assertEqual(like, Like(like_off))
        self.assertEqual(like.is_on(), False)
        self.assertEqual(like.get_total_likes(), 10)
        self.assertEqual(mock.call(f"SELECT"
                                   f"(SELECT COUNT(*) FROM likes WHERE comment_id = 'id_comment') AS total,"
                                   f"(SELECT COUNT(*) FROM likes WHERE user_id = 2 "
                                   f"and comment_id = 'id_comment' ) AS personal;"),
                         pool.fetch.mock_calls[0])

    async def test_switching_on_to_off(self):
        pool = AsyncMock()
        pool.fetch = AsyncMock()
        like_on = LikeOn(2, "id_comment", 10, pool)
        like = Like(like_on)
        self.assertTrue(type(like.like) == LikeOn)
        self.assertEqual(like.is_on(), True)
        self.assertEqual(like.get_total_likes(), 10)
        await like.switch()
        self.assertTrue(type(like.like) == LikeOff)
        self.assertEqual(like.is_on(), False)
        self.assertEqual(like.get_total_likes(), 9)
        self.assertEqual(mock.call(f"DELETE FROM likes WHERE "
                                   f"user_id = 2 AND comment_id = 'id_comment';"),
                         pool.fetch.mock_calls[0])

    async def test_switching_off_to_on(self):
        pool = AsyncMock()
        pool.fetch = AsyncMock()
        like_on = LikeOff(2, "id_comment", 10, pool)
        like = Like(like_on)
        self.assertTrue(type(like.like) == LikeOff)
        self.assertEqual(like.is_on(), False)
        self.assertEqual(like.get_total_likes(), 10)
        await like.switch()
        self.assertTrue(type(like.like) == LikeOn)
        self.assertEqual(like.is_on(), True)
        self.assertEqual(like.get_total_likes(), 11)
        self.assertEqual(mock.call(f"INSERT INTO likes (user_id, comment_id) "
                                   f"values (2, 'id_comment');"),
                         pool.fetch.mock_calls[0])


if __name__ == "__main__":
    unittest.main()
