import unittest

from gou2tool.util import WebHookUtil


class TestDemo(unittest.TestCase):

    def test_insert(self):
        WebHookUtil.send(
            "https://oapi.dingtalk.com/robot/send?access_token=6eb7c4a05da8552f740e9912b488a91a56b958eb191ab2c84783389ac6f8a559",
            {
                'msgtype': 'text',
                'text': {
                    'content': "1111"
                }
            },
            "SEC745aba3ccb27eba9e72e73de98649624bd9630085e708eb939456fa5ca2664c4")
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
