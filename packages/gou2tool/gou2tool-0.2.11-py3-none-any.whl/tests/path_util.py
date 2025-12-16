import unittest

from src.main.py.gou2tool.util.PathUtil import PathUtil

class TestDemo(unittest.TestCase):
    def test_simple_uuid(self):
        print(PathUtil.goutool_path())
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()