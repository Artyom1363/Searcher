import unittest
from searcher.elastic_algo import client

# print("tests was ran")


class TestElasticConnection(unittest.TestCase):
    def test_client(self):
        self.assertTrue(type(client.info()) is dict)


class TestElasticAlgo(unittest.TestCase):
    """

    """
    # def setUp(self):
        

    def test_adding_list(self):

        pass



if __name__ == "__main__":
    unittest.main()