import unittest

from gou2tool.util import StrUtil


class TestDemo(unittest.TestCase):

    def test_insert(self):
        print(StrUtil.calculate_similarity("湖北省武汉市武昌区楚汉路18号武汉中央文化区k4地块一期k4-2-5栋1-2层14-15室",
                                           "湖北省武汉市武昌区楚汉路武汉中央文化区地块一期k4-1-1栋"))
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
