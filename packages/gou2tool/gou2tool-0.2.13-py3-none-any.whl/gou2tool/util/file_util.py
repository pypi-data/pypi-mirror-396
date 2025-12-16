import os
import json


class FileUtil:

    @staticmethod
    def write(path, content):
        """写入内容到文件（覆盖模式）"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)

    @staticmethod
    def append(path, content):
        """
        追加内容到文件末尾

        Args:
            path (str): 文件路径
            content (str): 要追加的内容
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'a', encoding='utf-8') as file:
            file.write(content)

    @staticmethod
    def append_line(path, content):
        """
        追加一行内容到文件末尾（自动添加换行符）

        Args:
            path (str): 文件路径
            content (str): 要追加的行内容
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'a', encoding='utf-8') as file:
            file.write(content + '\n')

    @staticmethod
    def read_json(path):
        """
        读取JSON文件并返回解析后的数据

        Args:
            path (str): JSON文件路径

        Returns:
            dict|list: 解析后的JSON数据
        """
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)

    @staticmethod
    def write_json(path, data, ensure_ascii=False, indent=2):
        """
        将数据写入JSON文件

        Args:
            path (str): JSON文件路径
            data (dict|list): 要写入的JSON数据
            ensure_ascii (bool): 是否确保ASCII编码，默认False
            indent (int): 缩进空格数，默认2
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=ensure_ascii, indent=indent)
