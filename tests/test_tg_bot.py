import unittest
from unittest import mock
from unittest.mock import AsyncMock
from tg_bot.handlers import show_topic


class TestTGBot(unittest.IsolatedAsyncioTestCase):

    async def test_show_topic(self):
        with mock.patch("search.elastic_searcher.ElasticSearcher.get_topic_by_id") as get_topic_mock:
            get_topic_mock.return_value = "some string"
            callback = AsyncMock()
            callback.data = "questionScale_123"
            callback.answer = AsyncMock()
            await show_topic(callback)
            self.assertEqual(mock.call(text='some string', show_alert=True),
                             callback.answer.mock_calls[0])

            self.assertEqual(mock.call('123'), get_topic_mock.mock_calls[0])


if __name__ == "__main__":
    unittest.main()
