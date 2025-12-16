import unittest

from gou2tool.util import SQLUtil


class TestDemo(unittest.TestCase):

    def test_insert(self):
        print(SQLUtil.update("crm_organizations", {
            "lat": 1,
            "lon": 1,
            "name": None,
            "desc": "'adq'qa",
            "phone": ["11", "22'2"],
            "dict": {'a': 1, 'b': "a'"}
        }, {"id": 1, "ide": "2'"}))
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
