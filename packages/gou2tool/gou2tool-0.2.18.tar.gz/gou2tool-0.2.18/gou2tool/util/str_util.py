

class StrUtil:

    @staticmethod
    def calculate_similarity(str1, str2):
        """
        计算两个字符串的相似度，返回百分比

        Args:
            str1 (str): 第一个字符串
            str2 (str): 第二个字符串

        Returns:
            float: 相似度百分比 (0-100)
        """
        if not str1 and not str2:
            return 100.0
        if not str1 or not str2:
            return 0.0

        # 转换为小写进行比较
        s1, s2 = str1.lower(), str2.lower()
        m, n = len(s1), len(s2)

        # 创建DP表并计算编辑距离
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        # 初始化边界条件
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        # 填充DP表
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = min(
                        dp[i - 1][j] + 1,  # 删除
                        dp[i][j - 1] + 1,  # 插入
                        dp[i - 1][j - 1] + 1  # 替换
                    )

        # 计算相似度百分比
        distance = dp[m][n]
        max_len = max(len(s1), len(s2))
        similarity = (1 - distance / max_len) * 100
        return round(similarity, 2)

    @staticmethod
    def has_empty(*args):
        """
        检查传入的参数中是否有空值(None, '', [], {}, 等)

        Args:
            *args: 可变参数列表

        Returns:
            bool: 如果有任何参数为空则返回True，否则返回False
        """
        for arg in args:
            if not arg:
                return True
        return False

    @staticmethod
    def lower_case(text):
        """
        将字符串转换为小写格式

        Args:
            text (str): 需要转换的字符串

        Returns:
            str: 转换后的小写字符串
        """
        if text is None:
            return None
        return str(text).lower()

    @staticmethod
    def upper_case(text):
        """
        将字符串转换为大写格式

        Args:
            text (str): 需要转换的字符串

        Returns:
            str: 转换后的大写字符串
        """
        if text is None:
            return None
        return str(text).upper()

    @staticmethod
    def lower_first(text):
        """
        将字符串的第一个字符转换为小写

        Args:
            text (str): 需要转换的字符串

        Returns:
            str: 首字符小写的字符串
        """
        if not text:
            return text
        return text[0].lower() + text[1:]

    @staticmethod
    def upper_first(text):
        """
        将字符串的第一个字符转换为大写

        Args:
            text (str): 需要转换的字符串

        Returns:
            str: 首字符大写的字符串
        """
        if not text:
            return text
        return text[0].upper() + text[1:]

    @staticmethod
    def upper_words(text):
        """
        将字符串中每个单词的首字母转换为大写（驼峰式标题格式）

        Args:
            text (str): 需要转换的字符串

        Returns:
            str: 每个单词首字母大写的字符串
        """
        if not text:
            return text
        return text.title()

    @staticmethod
    def has_not_empty(*args):
        """
        检查传入的参数中是否有非空值（至少有一个不为空）

        Args:
            *args: 可变参数列表

        Returns:
            bool: 如果有任何参数不为空则返回True，否则返回False
        """
        for arg in args:
            if arg:
                return True
        return False

    @staticmethod
    def is_string(value):
        """
        检查值是否为字符串类型

        Args:
            value: 需要检查的值

        Returns:
            bool: 如果是字符串类型返回True，否则返回False
        """
        return isinstance(value, str)

    @staticmethod
    def is_not_string(value):
        """
        检查值是否不为字符串类型

        Args:
            value: 需要检查的值

        Returns:
            bool: 如果不是字符串类型返回True，否则返回False
        """
        return not isinstance(value, str)

    @staticmethod
    def replace(search, replace, subject):
        """
        字符串替换

        Args:
            search: 匹配值
            replace: 替换值
            subject: 替换内容

        Returns:
            str: 替换后的字符串
        """
        if subject is None:
            return None
        return str(subject).replace(search, replace)

    @staticmethod
    def preg_replace(pattern, replace, subject):
        """
        字符串正则表达式替换

        Args:
            pattern: 匹配值（正则表达式）
            replace: 替换值
            subject: 替换内容

        Returns:
            str: 正则替换后的字符串
        """
        import re
        if subject is None:
            return None
        return re.sub(pattern, replace, str(subject))

    @staticmethod
    def equals(str1, str2):
        """
        两个字符串是否相等

        Args:
            str1: 第一个字符串
            str2: 第二个字符串

        Returns:
            bool: 如果两个字符串相等返回True，否则返回False
        """
        return str(str1) == str(str2)

    @staticmethod
    def not_equals(str1, str2):
        """
        两个字符串是否不相等

        Args:
            str1: 第一个字符串
            str2: 第二个字符串

        Returns:
            bool: 如果两个字符串不相等返回True，否则返回False
        """
        return not StrUtil.equals(str1, str2)

    @staticmethod
    def trim(string):
        """
        字符串去空格

        Args:
            string: 需要去空格的字符串

        Returns:
            str: 去除首尾空格的字符串
        """
        if string is None:
            return None
        return str(string).strip()

    @staticmethod
    def split(string, separator):
        """
        字符串转数组（分割字符串）

        Args:
            string: 需要分割的字符串
            separator: 分隔符

        Returns:
            list: 分割后的字符串列表
        """
        if string is None:
            return []
        return str(string).split(separator)

    @staticmethod
    def join(array, separator=""):
        """
        数组转字符串

        Args:
            array: 需要连接的数组
            separator: 分隔符，默认为空字符串

        Returns:
            str: 连接后的字符串
        """
        if array is None:
            return ""
        return separator.join(str(item) for item in array)

    @staticmethod
    def sub(string, start, length=None):
        """
        字符串截取

        Args:
            string: 需要截取的字符串
            start: 开始位置
            length: 截取长度（可选）

        Returns:
            str: 截取后的字符串
        """
        if string is None:
            return None
        if length is None:
            return str(string)[start:]
        return str(string)[start:start + length]

    @staticmethod
    def last_char(string):
        """
        获取字符串最后一个字符

        Args:
            string: 输入字符串

        Returns:
            str: 字符串的最后一个字符
        """
        if not string:
            return ""
        return str(string)[-1]

    @staticmethod
    def starts_with(string, prefix):
        """
        方法用于检索字符串是否以指定字符串开头

        Args:
            string: 需要检查的字符串
            prefix: 前缀字符串或字符串列表

        Returns:
            bool: 如果字符串以指定前缀开头返回True，否则返回False
        """
        if not string:
            return False

        if isinstance(prefix, (list, tuple)):
            for item in prefix:
                if str(string).startswith(str(item)):
                    return True
            return False
        else:
            return str(string).startswith(str(prefix))

    @staticmethod
    def ends_with(string, suffix):
        """
        方法用于检索字符串是否以指定字符串结尾

        Args:
            string: 需要检查的字符串
            suffix: 后缀字符串或字符串列表

        Returns:
            bool: 如果字符串以指定后缀结尾返回True，否则返回False
        """
        if not string:
            return False

        if isinstance(suffix, (list, tuple)):
            for item in suffix:
                if str(string).endswith(str(item)):
                    return True
            return False
        else:
            return str(string).endswith(str(suffix))

    @staticmethod
    def rm_first_word(string):
        """
        移除字符串首字母

        Args:
            string: 输入字符串

        Returns:
            str: 移除首字母后的字符串
        """
        if not string:
            return string
        return str(string)[1:]

    @staticmethod
    def hide(string, start_include, end_exclude):
        """
        替换指定字符串的指定区间内字符为"*"
        俗称：脱敏功能

        Args:
            string: 输入字符串
            start_include: 开始位置（包含）
            end_exclude: 结束位置（不包含）

        Returns:
            str: 替换后的字符串

        Examples:
            StrUtil.hide(None, *, *) = None
            StrUtil.hide("", 0, *) = ""
            StrUtil.hide("jackduan@163.com", -1, 4) = "****duan@163.com"
            StrUtil.hide("jackduan@163.com", 2, 3) = "ja*kduan@163.com"
            StrUtil.hide("jackduan@163.com", 3, 2) = "jackduan@163.com"
            StrUtil.hide("jackduan@163.com", 16, 16) = "jackduan@163.com"
            StrUtil.hide("jackduan@163.com", 16, 17) = "jackduan@163.com"
        """
        # 处理空值情况
        if string is None or string == "":
            return string

        str_val = str(string)
        length = len(str_val)

        # 处理负数开始位置，转换为从末尾计算
        if start_include < 0:
            start_include = length + start_include

        # 边界检查：如果开始位置大于等于结束位置，或者超出字符串范围，则不处理
        if start_include >= end_exclude or start_include >= length or end_exclude <= 0:
            return str_val

        # 确保开始位置不小于0
        start_include = max(0, start_include)
        # 确保结束位置不大于字符串长度
        end_exclude = min(length, end_exclude)

        # 如果处理范围无效，则返回原字符串
        if start_include >= end_exclude:
            return str_val

        # 计算需要替换的字符数量
        replace_length = end_exclude - start_include

        # 构造替换字符串
        replacement = '*' * replace_length

        # 执行替换操作
        return str_val[:start_include] + replacement + str_val[end_exclude:]
