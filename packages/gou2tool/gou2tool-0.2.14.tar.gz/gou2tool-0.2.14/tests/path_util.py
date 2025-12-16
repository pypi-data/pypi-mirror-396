import unittest

from gou2tool.util import PathUtil

class TestDemo(unittest.TestCase):
    def test_simple_uuid(self):
        print(PathUtil.project_path())
        print(PathUtil.path("project:/tests/id_util.py"))
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()