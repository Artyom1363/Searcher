import unittest
from unittest import mock
from unittest.mock import AsyncMock
from src.data_types.fvrt import Favorite, FavoriteOn, FavoriteOff


class TestFavorites(unittest.IsolatedAsyncioTestCase):
    async def test_creating_favorite_on(self):
        pool = AsyncMock()
        pool.fetch = AsyncMock(return_value=[[1]])
        favorite = await Favorite.get(1, "comment_id", pool)
        favorite_on = FavoriteOn(1, "comment_id", pool)
        self.assertEqual(favorite, Favorite(favorite_on))
        self.assertEqual(favorite.is_on(), True)
        self.assertEqual(mock.call(
            "SELECT COUNT(*) as is_on "
            "FROM favorites WHERE user_id = 1 AND comment_id = 'comment_id';"),
                         pool.fetch.mock_calls[0])

    async def test_creating_favorite_off(self):
        pool = AsyncMock()
        pool.fetch = AsyncMock(return_value=[[0]])
        favorite = await Favorite.get(2, "id_comment", pool)
        favorite_off = FavoriteOff(2, "id_comment", pool)
        self.assertEqual(favorite, Favorite(favorite_off))
        self.assertEqual(favorite.is_on(), False)
        self.assertEqual(mock.call(
            "SELECT COUNT(*) as is_on "
            "FROM favorites WHERE user_id = 2 AND comment_id = 'id_comment';"),
                         pool.fetch.mock_calls[0])

    async def test_switching_on_to_off(self):
        pool = AsyncMock()
        pool.fetch = AsyncMock()
        favorite_on = FavoriteOn(2, "id_comment", pool)
        favorite = Favorite(favorite_on)
        self.assertTrue(isinstance(favorite.favorite, FavoriteOn))
        self.assertEqual(favorite.is_on(), True)
        await favorite.switch()
        self.assertTrue(isinstance(favorite.favorite, FavoriteOff))
        self.assertEqual(favorite.is_on(), False)
        self.assertEqual(mock.call(
            "DELETE FROM favorites WHERE "
            "user_id = 2 AND comment_id = 'id_comment';"),
                         pool.fetch.mock_calls[0])

    async def test_switching_off_to_on(self):
        pool = AsyncMock()
        pool.fetch = AsyncMock()
        favorite_on = FavoriteOff(2, "id_comment", pool)
        favorite = Favorite(favorite_on)
        self.assertTrue(isinstance(favorite.favorite, FavoriteOff))
        self.assertEqual(favorite.is_on(), False)
        await favorite.switch()
        self.assertTrue(isinstance(favorite.favorite, FavoriteOn))
        self.assertEqual(favorite.is_on(), True)
        self.assertEqual(mock.call(
            "INSERT INTO favorites (user_id, comment_id) "
            "VALUES (2, 'id_comment');"),
                         pool.fetch.mock_calls[0])


if __name__ == "__main__":
    unittest.main()
