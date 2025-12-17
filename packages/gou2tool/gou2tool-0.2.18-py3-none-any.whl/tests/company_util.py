import unittest

from gou2tool.util.company_util import CompanyUtil


class TestDemo(unittest.TestCase):
    def test_name(self):
        company_list = [
            "台山市台城向日葵美业工作室（个体工商户）",
            "北京美宸伟业住房租赁有限责任公司",
            "大连美林达企业管理咨询有限公司",
            "佛山美林达企业管理咨询有限公司",
            "上海美林达企业管理咨询有限公司",
            "海口诺美施企业管理有限公司",
            "经开区悦己美业店（个体工商户）",
            "昆明倾诚悦秀美业品牌管理有限公司第一分公司",
            "青岛澜绮美业科技有限公司",
            "上海白钥美品农业发展有限公司",
            "宁波市鄞州中河美丁酒业商行（个体工商户）",
        ]
        for company in company_list:
            print(CompanyUtil.name(company), "=>", company)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
