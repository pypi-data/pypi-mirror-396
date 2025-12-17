import unittest

from gou2tool.util import IdUtil


class TestDemo(unittest.TestCase):
    def test_simple_uuid(self):
        print(IdUtil.simple_uuid())
        self.assertTrue(True)

    def test_random_uuid(self):
        print(IdUtil.random_uuid())
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()