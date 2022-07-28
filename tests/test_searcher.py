import unittest
from ..lib.elastic_algo import client

# print("tests was ran")


class TestElasticConnection(unittest.TestCase):
    def test_client(self):
        print(client.info())


class TestElasticAlgo(unittest.TestCase):
    """

    """
    # def setUp(self):
        

    def test_adding_list(self):
        self.assertEqual(self.array + [1, 2], CustomList([2, 4, 3]))
        self.assertEqual(self.array + [1, 2, 3, 4], CustomList([2, 4, 6, 4]))
    
    def test_subtraction(self):
        self.assertEqual(self.array - [1, 2], CustomList([0, 0, 3]))
        self.assertEqual(self.array - [1, 2, 3, 4], CustomList([0, 0, 0, -4]))
    
    def test_equal(self):
        self.assertTrue(self.array == [3, 2, 1])
        self.assertTrue(self.array == [6])
        self.assertEqual(self.array, [3, 2, 1])
    
    def test_to_str(self):
        self.assertEqual(str(self.array), "[1, 2, 3] sum: 6")


if __name__ == "__main__":
    unittest.main()