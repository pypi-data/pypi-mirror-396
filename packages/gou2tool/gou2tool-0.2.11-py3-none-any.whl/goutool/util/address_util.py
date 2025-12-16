import os
import json

class AddressUtil:

    @staticmethod
    def parse(address):
        """
        解析地址字符串，返回结构化地址信息

        Args:
            address (str): 完整地址字符串

        Returns:
            dict: 包含省、市、区等信息的字典
        """
        if not address:
            return {}

        # 初始化结果字典
        result = {
            "province": "",
            "city": "",
            "district": "",
            "street": "",
            "detail": ""
        }

        # 获取省市区数据用于匹配
        province_city_data = AddressUtil.get_province_city_district_tree()

        # 简化的地址解析逻辑（实际应用中可能需要更复杂的匹配规则）
        # 1. 提取省份信息
        for province_data in province_city_data:
            province_name = province_data.get("province", "")
            if province_name and province_name in address:
                result["province"] = province_name
                # 从地址中移除已匹配的省份信息
                address = address.replace(province_name, "", 1)
                break

        # 2. 提取城市信息
        for province_data in province_city_data:
            if "children" in province_data:
                for city_data in province_data["children"]:
                    city_name = city_data.get("city", "")
                    if city_name and city_name in address:
                        result["city"] = city_name
                        # 从地址中移除已匹配的城市信息
                        address = address.replace(city_name, "", 1)
                        break

        # 3. 提取区域信息
        for province_data in province_city_data:
            if "children" in province_data:
                for city_data in province_data["children"]:
                    if "children" in city_data:
                        for district_data in city_data["children"]:
                            district_name = district_data.get("district", "")
                            if district_name and district_name in address:
                                result["district"] = district_name
                                # 从地址中移除已匹配的区域信息
                                address = address.replace(district_name, "", 1)
                                break

        # 4. 剩余部分作为街道和详细地址
        result["street"] = address.strip()
        result["detail"] = address.strip()

        return result


    @staticmethod
    def has_province_city_district():
        """
        判断地址是否包含省市区信息

        Returns:
            bool: 如果包含省市区信息返回True，否则返回False
        """
        # TODO: 实现判断逻辑
        return False


    @staticmethod
    def has_province_city():
        """
        判断地址是否包含省市信息

        Returns:
            bool: 如果包含省市信息返回True，否则返回False
        """
        # TODO: 实现判断逻辑
        return False


    @staticmethod
    def get_province_city_district_tree():
        """
        获取省市区三级树形结构数据

        Returns:
            list: 省市区树形结构数据
        """
        # TODO: 实现获取省市区树形结构的逻辑
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(__file__)
        # 构建数据文件路径
        data_file_path = os.path.join(current_dir, 'data', 'pca-code.json')

        # 读取JSON文件
        with open(data_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        return data


    @staticmethod
    def get_province_city_district_street_tree():
        """
        获取省市区街道四级树形结构数据

        Returns:
            list: 省市区街道树形结构数据
        """
        # TODO: 实现获取省市区街道树形结构的逻辑
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(__file__)
        # 构建数据文件路径
        data_file_path = os.path.join(current_dir, 'data', 'pcas-code.json')

        # 读取JSON文件
        with open(data_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        return data
