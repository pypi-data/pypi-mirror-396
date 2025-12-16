import unittest

from src.main.py.gou2tool.util.PhoneUtil import PhoneUtil


class TestDemo(unittest.TestCase):

    def test_is_phone(self):
        print(PhoneUtil.is_phone('11571631036'))
        self.assertTrue(True)

    def test_is_tel(self):
        print(PhoneUtil.is_tel('111-58597128'))
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()