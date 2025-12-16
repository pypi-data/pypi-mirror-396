import json

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
