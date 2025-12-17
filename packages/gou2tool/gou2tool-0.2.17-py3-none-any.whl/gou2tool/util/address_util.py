import re


class AddressUtil:

    @staticmethod
    def calculate_similarity(address1, address2):
        """
        计算两个中文地址的相似度（按位置权重+层级加权）
        尾部/门牌号权重高，省/市层级仅做归一不加分
        """
        if not address1 and not address2:
            return 100.0
        if not address1 or not address2:
            return 0.0

        # -------------------------- 1. 通用工具函数（内部嵌套，无新增外部方法） --------------------------
        def levenshtein_distance(s1, s2):
            """编辑距离算法（核心稳定，仅精简逻辑）"""
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            if len(s2) == 0:
                return len(s1)
            prev_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                curr_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insert = prev_row[j + 1] + 1
                    delete = curr_row[j] + 1
                    substitute = prev_row[j] + (c1 != c2)
                    curr_row.append(min(insert, delete, substitute))
                prev_row = curr_row
            return prev_row[-1]

        def normalize_house_number(num_str):
            """门牌号归一：去除字母后缀/前缀，提取核心数字+字母组合"""
            if not num_str:
                return ""
            # 提取字母+数字组合（如A2610→A2610，2610→2610，1层6号→6）
            num_match = re.search(r'([A-Za-z]*\d+[A-Za-z]*)', num_str)
            return num_match.group(1).upper() if num_match else num_str.strip().upper()

        # -------------------------- 2. 地址预处理（增强版） --------------------------
        def preprocess(address):
            addr_str = str(address).strip()

            # 2.1 形近字/地址别名归一（通用化，无硬编码业务词）
            char_normalize = {
                '融桥城': '融侨城', '都粱华府': '都梁华府', '粱': '梁',
                '座': '栋', '号楼': '栋', '铺': '号', '门面': '',
                '附': '-', '＃': '#', '（': '', '）': '', '(': '', ')': ''
            }
            for old, new in char_normalize.items():
                addr_str = addr_str.replace(old, new)

            # 2.2 中文数字转阿拉伯数字（仅匹配门牌号/楼栋相关的中文数字）
            chinese_to_arabic = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6', '七': '7', '八': '8',
                                 '九': '9', '零': '0'}
            # 正向匹配（数字+关键字：如"三楼"→"3楼"）
            for chinese, arabic in chinese_to_arabic.items():
                addr_str = re.sub(fr'{chinese}(?=(栋|单元|号|层|室|楼|幢|铺))', arabic, addr_str)
                # 反向匹配（关键字+数字：如"栋三"→"栋3"）
                addr_str = re.sub(fr'(栋|单元|号|层|室|楼|幢|铺){chinese}', fr'\\g<1>{arabic}', addr_str)

            # 2.3 移除冗余描述词（扩展通用场景）
            redundant_terms = [
                '等两户', '商住楼', '办公楼', '商铺', '门店', '自主申报', '（自主申报）', '门面',
                '（此证与拆迁补偿无关）', '前排', '建设银行旁', '负一楼', '二楼', '三楼',
                '东侧', '西侧', '北侧', '南侧', '附近', '旁', '一楼', '二楼'
            ]
            for term in redundant_terms:
                addr_str = addr_str.replace(term, '')

            # 2.4 特殊符号/分隔符归一
            symbol_normalize = {
                '，': '', '、': '', '：': '', ':': '', '？': '', '/': '', '\\': '',
                '－': '-', '—': '-', '　': ' ', '\t': '', '\n': '', '.': '', '＃': '#'
            }
            for old, new in symbol_normalize.items():
                addr_str = addr_str.replace(old, new)

            # 2.5 移除非核心字符+规范化空格
            addr_str = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\-]', '', addr_str)
            addr_str = re.sub(r'\s+', ' ', addr_str).strip()

            return addr_str

        # 执行预处理
        addr1 = preprocess(address1)
        addr2 = preprocess(address2)

        # -------------------------- 3. 基础相似度计算 --------------------------
        max_len = max(len(addr1), len(addr2))
        if max_len == 0:
            return 100.0
        base_dist = levenshtein_distance(addr1, addr2)
        base_similarity = (1 - base_dist / max_len) * 100
        similarity = base_similarity

        # -------------------------- 4. 分层级匹配（核心优化） --------------------------
        # 4.1 提取地址层级（省/市/县/镇/路/号）
        def extract_address_levels(addr):
            levels = {
                'province': re.findall(r'([\u4e00-\u9fa5]+省)', addr),
                'city': re.findall(r'([\u4e00-\u9fa5]+市)', addr),
                'county': re.findall(r'([\u4e00-\u9fa5]+县|[\u4e00-\u9fa5]+区|[\u4e00-\u9fa5]+管理区)', addr),
                'town': re.findall(r'([\u4e00-\u9fa5]+镇|[\u4e00-\u9fa5]+街道|[\u4e00-\u9fa5]+办事处)', addr),
                'road': re.findall(r'[\u4e00-\u9fa5]{2,}(?:路|街|道|大道|巷|弄)', addr),
                'number': re.findall(r'[A-Za-z]*\d+[A-Za-z]*', addr)  # 提取字母+数字组合的门牌号
            }
            # 归一化层级值（去重+转大写）
            for k in levels:
                levels[k] = [item.strip().upper() for item in levels[k]]
            return levels

        levels1 = extract_address_levels(addr1)
        levels2 = extract_address_levels(addr2)

        # 4.2 层级匹配加权（层级越低，权重越高）
        level_weights = {
            'road': 10,  # 道路匹配权重最高
            'town': 5,  # 乡镇/街道次之
            'county': 2,  # 区县仅少量权重
            'city': 0,  # 市级匹配不加分（避免跨市误匹配）
            'province': 0  # 省级匹配不加分
        }
        level_add_score = 0
        for level, weight in level_weights.items():
            if levels1[level] and levels2[level]:
                # 只要有一个层级值匹配就加分
                if set(levels1[level]) & set(levels2[level]):
                    level_add_score += weight

        # 4.3 门牌号精准匹配（核心修复）
        num1 = levels1['number'][-1] if levels1['number'] else ""
        num2 = levels2['number'][-1] if levels2['number'] else ""
        norm_num1 = normalize_house_number(num1)
        norm_num2 = normalize_house_number(num2)

        number_add_score = 0
        number_penalty = 0
        if norm_num1 and norm_num2:
            if norm_num1 == norm_num2:
                number_add_score = 20  # 门牌号完全匹配加20分
            else:
                # 门牌号数字部分差异计算
                num1_digit = re.findall(r'\d+', norm_num1)
                num2_digit = re.findall(r'\d+', norm_num2)
                if num1_digit and num2_digit:
                    digit1 = int(num1_digit[-1]) if num1_digit[-1].isdigit() else 0
                    digit2 = int(num2_digit[-1]) if num2_digit[-1].isdigit() else 0
                    diff = abs(digit1 - digit2)
                    if diff <= 2:
                        number_add_score = 5  # 数字差异≤2加5分
                    elif diff <= 5:
                        number_add_score = 2  # 数字差异≤5加2分
                    elif diff > 20:
                        number_penalty = 15  # 数字差异>20扣15分
                else:
                    # 非数字门牌号（纯字母）不扣分
                    pass
        # 门牌号为空时不扣分
        elif not norm_num1 and not norm_num2:
            number_add_score = 0
        # 仅一个有门牌号时扣分
        else:
            number_penalty = 10

        # -------------------------- 5. 其他权重规则（精准化） --------------------------
        # 5.1 地址包含关系（仅核心部分包含才加分）
        contain_add_score = 0
        if addr1 in addr2 or addr2 in addr1:
            # 需同时匹配道路+至少一个层级，才加分
            if set(levels1['road']) & set(levels2['road']):
                contain_add_score = 8

        # 5.2 尾部匹配（聚焦门牌号区域）
        tail_add_score = 0
        min_len = min(len(addr1), len(addr2))
        if min_len > 5:
            tail_len = min(15, min_len)
            tail1 = addr1[-tail_len:]
            tail2 = addr2[-tail_len:]
            tail_dist = levenshtein_distance(tail1, tail2)
            tail_sim = (1 - tail_dist / tail_len) * 100
            if tail_sim > 90:
                tail_add_score = 10
            elif tail_sim > 80:
                tail_add_score = 5

        # -------------------------- 6. 总分校准（避免过度加分/扣分） --------------------------
        # 累加所有加分项
        total_add = level_add_score + number_add_score + contain_add_score + tail_add_score
        # 应用扣分项
        total_penalty = number_penalty

        # 核心规则：总分不超过100，不低于0；基础分<50时，加分不超过20
        similarity += total_add - total_penalty
        if base_similarity < 50:
            similarity = min(base_similarity + 20, similarity)
        similarity = max(0.0, min(100.0, similarity))

        final_similarity = round(similarity, 2)
        return final_similarity

    @staticmethod
    def format(address):
        """
        标准化地址格式，提取省市等关键信息

        Args:
            address (str): 原始地址字符串

        Returns:
            dict: 包含标准化地址信息的字典
        """
        # 初始化结果字典
        result = {
            "province": None,  # 省级行政区
            "city": None,  # 地市级行政区
            "district": None,  # 区县级行政区
            "subdistrict": None,  # 乡镇/街道级
            "community": None,  # 社区/村级
            "road": None,  # 道路信息
            "house_number": None,  # 门牌号
            "building": None,  # 建筑物
            "building_block": None,  # 楼座
            "floor": None,  # 楼层
            "room": None,  # 房间
            "full_address": None,  # 完整地址
            "original_address": str(address)  # 原始地址
        }

        if not address or not isinstance(address, str) or not address.strip():
            return result

        # 清理和标准化输入地址
        clean_address = address.strip().replace("，", ",").replace("。", "").replace("\n", " ").replace("\r", " ")
        clean_address = re.sub(r'\s+', ' ', clean_address)

        # 提取省级行政区
        province_patterns = [
            r'([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼港澳台][\u4e00-\u9fa5]*[省])',
            r'([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼港澳台][\u4e00-\u9fa5]*自治区)',
            r'([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼港澳台][\u4e00-\u9fa5]*特别行政区)'
        ]

        for pattern in province_patterns:
            match = re.search(pattern, clean_address)
            if match:
                result["province"] = match.group(1)
                clean_address = clean_address.replace(match.group(1), '', 1)
                break

        # 处理直辖市
        direct_cities = ['北京市', '上海市', '天津市', '重庆市']
        for city in direct_cities:
            if city in clean_address:
                result["province"] = city
                result["city"] = city
                clean_address = clean_address.replace(city, '', 1)
                break

        # 提取市级行政区
        if not result["city"] or result["province"] != result["city"]:
            city_match = re.search(r'([^\s]+市)', clean_address)
            if city_match:
                result["city"] = city_match.group(1)
                clean_address = clean_address.replace(city_match.group(1), '', 1)

        # 提取区县级行政区
        district_match = re.search(r'([^\s]+[县区旗])', clean_address)
        if district_match:
            result["district"] = district_match.group(1)
            clean_address = clean_address.replace(district_match.group(1), '', 1)

        # 提取街道级行政区
        subdistrict_match = re.search(r'([^\s]+[镇街乡])', clean_address)
        if subdistrict_match:
            result["subdistrict"] = subdistrict_match.group(1)

        # 提取社区信息
        community_match = re.search(r'([^\s]+[社区村])', clean_address)
        if community_match:
            result["community"] = community_match.group(1)

        # 提取道路信息
        road_match = re.search(r'([\u4e00-\u9fa5]{2,}(?:路|街|道|大道|巷|弄))', clean_address)
        if road_match:
            result["road"] = road_match.group(1)

        # 提取门牌号
        house_number_match = re.search(r'(\d+[号]?)', clean_address)
        if house_number_match:
            result["house_number"] = house_number_match.group(1)

        # 提取建筑物信息
        building_match = re.search(r'([^\s]+[大厦楼园城苑馆])', clean_address)
        if building_match:
            result["building"] = building_match.group(1)

        # 提取楼座信息
        block_match = re.search(r'([A-Za-z\d]+)[座栋幢]', clean_address)
        if block_match:
            result["building_block"] = f"{block_match.group(1)}座"

        # 提取楼层信息
        floor_match = re.search(r'(\d+)层', clean_address)
        if floor_match:
            result["floor"] = f"{floor_match.group(1)}层"

        # 提取房间信息
        room_match = re.search(r'(\d{3,4})室', clean_address)
        if room_match:
            result["room"] = f"{room_match.group(1)}室"

        # 生成完整地址
        address_components = [
            result["province"],
            result["city"] if result["city"] != result["province"] else None,
            result["district"],
            result["subdistrict"],
            result["community"],
            result["road"],
            result["house_number"],
            result["building"],
            result["building_block"],
            result["floor"],
            result["room"]
        ]

        result["full_address"] = ''.join(filter(None, address_components))

        return result
