import unittest
from search.elastic_searcher import ElasticSearcher
from search.config import USER, ELASTIC_PASSWORD, PATH_TO_CRT, ELASTIC_URL

from data_types.values import Sentence
from data_types.post import Post

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import time


class TestElasticAlgo(unittest.TestCase):
    """
    This class tests:
    1. Connecting to elasticsearch server
    2. ElasticSearcher class by creating topics and comments with Value as Sentence on server
    3. Time of creating data on server
    """

    def setUp(self):
        self.client = Elasticsearch(
            ELASTIC_URL,
            ca_certs=PATH_TO_CRT,
            basic_auth=(USER, ELASTIC_PASSWORD)
        )
        self.index_topic = "test_topics"
        self.index_comments = "test_comments"

        # delete indexes
        self.client.indices.delete(index=self.index_topic, ignore=[400, 404])
        self.client.indices.delete(index=self.index_comments, ignore=[400, 404])

    def test_connection_to_server(self):
        self.assertTrue(type(self.client.info()) is dict)

    def test_adding_record(self):
        sentence1 = Sentence(sentence="test value")
        sentence2 = Sentence(sentence="test value2")
        post = Post(key="test key", values=[sentence1, sentence2])

        # adding data
        ElasticSearcher.add_record(post, index_topic=self.index_topic, index_comments=self.index_comments)

        # search added data
        time.sleep(1)
        response_topics = Search(index=self.index_topic, using=self.client).execute()
        response_comments = Search(index=self.index_comments, using=self.client).execute()
        self.assertEqual(len(response_topics), 1)
        self.assertEqual(response_topics[0]["title"], "test key")

        self.assertEqual(len(response_comments), 2)
        self.assertEqual(response_comments[0]["sentence"], "test value")
        self.assertEqual(response_comments[1]["sentence"], "test value2")

        # delete all data
        Search(index=self.index_topic, using=self.client).query().delete()
        Search(index=self.index_comments, using=self.client).query().delete()

        time.sleep(1)
        # check data on server
        response_topics = Search(index=self.index_topic, using=self.client).execute()
        response_comments = Search(index=self.index_comments, using=self.client).execute()
        self.assertEqual(len(response_topics), 0)
        self.assertEqual(len(response_comments), 0)

    def test_adding_without_comments(self):
        pass

    def test_getting_relevant(self):
        sentence1 = Sentence(sentence="Ответ к тесту")
        post = Post(key="тесты по физике", values=[sentence1])

        # adding data
        ElasticSearcher.add_record(post, index_topic=self.index_topic, index_comments=self.index_comments)

        time.sleep(1)
        relevant = ElasticSearcher.get_relevant_topics(message='физике тесты', using=self.client, index_topics=self.index_topic)
        self.assertEqual(relevant[0][0], "тесты по физике")
        self.assertNotEqual(relevant[0][1], "")

    def tearDown(self) -> None:
        # delete indexes
        self.client.indices.delete(index=self.index_topic, ignore=[400, 404])
        self.client.indices.delete(index=self.index_comments, ignore=[400, 404])


if __name__ == "__main__":
    unittest.main()
