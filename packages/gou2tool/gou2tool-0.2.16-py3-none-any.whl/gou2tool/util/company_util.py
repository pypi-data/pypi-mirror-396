# company_util.py
import re


class CompanyUtil:

    @staticmethod
    def name(value):
        """
        提取企业名称的核心部分，去除城市省份前缀、括号内容和企业后缀
        """
        if not value:
            return ""

        result = value

        # 1. 移除括号内的内容（如个体工商户、分支机构等）
        result = re.sub(r'[（(][^）)]*[)）]', '', result).strip()

        # 2. 移除分公司信息
        result = re.sub(r'第.+?分公司', '', result).strip()

        # 3. 移除城市/地区前缀（常见的地名开头）
        city_prefixes = [
            r'^北京市', r'^上海市', r'^天津市', r'^重庆市',
            r'^[\u4e00-\u9fa5]+省',  # 省份
            r'^[\u4e00-\u9fa5]+市',  # 城市
            r'^[\u4e00-\u9fa5]+区',  # 区县
            r'^[\u4e00-\u9fa5]+县',  # 县
            r'^[\u4e00-\u9fa5]+自治州',
            r'^[\u4e00-\u9fa5]+地区',
            r'^[\u4e00-\u9fa5]+盟',
            r'^经济技术开发区',
            r'^经开区',
            r'^北京', r'^上海', r'^天津', r'^重庆', r'^武汉', r'^襄阳', r'^南京', r'^长沙', r'^岳阳', r'^大连',
            r'^佛山', r'^海口', r'^西安', r'^长春', r'^郑州', r'^石家庄', r'^太原', r'^合肥', r'^南昌', r'^贵阳',
            r'^昆明', r'^拉萨', r'^银川', r'^拉萨', r'^兰州', r'^乌鲁木齐', r'^拉萨', r'^青岛', r'^均川', r'^随州',
            r'^潜江', r'^仙桃', r'^天门'
        ]

        # 按长度降序排列，确保优先匹配较长的前缀
        sorted_city_prefixes = sorted(city_prefixes, key=lambda x: len(x), reverse=True)

        for prefix in sorted_city_prefixes:
            result = re.sub(prefix, '', result).strip()

        # 4. 移除常见的企业后缀
        suffixes = [
            r'有限责任公司$', r'有限公司$', r'股份有限公司$',
            r'责任公司$', r'责任有限公司$', r'责任投资$', r'投资$',
            r'投资集团$', r'投资有限公司$', r'投资咨询$', r'投资机构$',
            r'科技有限公司', r'企业管理咨询$',
            r'企业管理咨询有限公司', r'品牌管理', r'农业发展',
            r'咨询', r'管理', r'教育', r'教育咨询', r'教育机构',
            r'教育咨询机构', r'酒业', r'企业管理有限公司', r'住房租赁',
            r'公司$', r'工作室$', r'商行$', r'店$', r'中心$',
            r'企业$', r'集团$', r'合作社$', r'酒业商行$', r'美业工作室$',
            r'美业品牌管理有限公司$', r'美容店$', r'美容美甲店$', r'美容养生会馆$',
            r'中式美容院$', r'化妆品店$', r'美容美甲工作室$', r'养生馆$', r'护肤中心$',
            r'康美容馆$', r'美颜中心$', r'化妆品销售店$', r'美容美体店$', r'美发店$',
            r'美容中心$', r'养生保健馆$', r'美甲店$', r'保健馆$', r'美容养生馆$',
            r'烫染造型室$', r'美容有限公司$', r'门诊部$', r'诊所$', r'美容诊所有限公司$',
            r'理发店$', r'健康管理中心$'
        ]

        # 按长度降序排列，确保优先匹配较长的后缀
        sorted_suffixes = sorted(suffixes, key=lambda x: len(x), reverse=True)

        for suffix in sorted_suffixes:
            result = re.sub(suffix, '', result).strip()

        return result if result else value
