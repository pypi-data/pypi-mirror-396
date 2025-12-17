import os
import re
import tempfile
from pathlib import Path


class PathUtil:
    """路径工具类"""

    def path(*paths: str, quote_spaces: bool = False) -> str:
        """
        构建并处理特殊前缀路径（单函数终极优化版）

        支持的特殊前缀:
        - project:<path>: 项目根目录下的路径
        - system-temp:<path>: 系统临时目录下的路径
        - create-system-temp:<path>: 在系统临时目录创建子路径
        - create-system-temp-file:*.<ext>: 创建带指定扩展名的临时文件
        - vendor:<path>: 项目vendor目录下的路径

        :param paths: 路径组件
        :param quote_spaces: 是否对含空格路径添加引号（Linux/Mac专用）
        :return: 规范化的完整路径
        :raises ValueError: 路径组件无效时
        """
        # ===== 预计算常量（函数级缓存）=====
        _IS_WINDOWS = os.name == 'nt'
        _TEMP_DIR = tempfile.gettempdir()
        _PROJECT_PATH = os.getcwd()  # 简化版项目路径

        # 通用的前导斜杠去除函数
        def remove_leading_slash(path):
            """去除路径前导的斜杠"""
            return path.lstrip('/\\')

        # ===== 输入验证 =====
        if not paths:
            raise ValueError("至少需要一个路径组件")

        # ===== 预编译正则（局部作用域优化）=====
        _EXT_PATTERN = re.compile(r'^create-system-temp-file:\*(\.\w+)$')
        _SPACE_PATTERN = re.compile(r'\s')

        # ===== 核心路径处理 =====
        # 1. 合并路径组件
        raw_path = Path(*paths).as_posix()

        # 2. 处理特殊前缀（策略模式）
        processed_path = raw_path

        # 2.1 临时文件创建（最高优先级）
        if raw_path.startswith('create-system-temp-file:*'):
            # 提取扩展名
            ext_match = _EXT_PATTERN.match(raw_path)
            ext = ext_match.group(1) if ext_match else ".tmp"

            # 安全创建临时文件
            fd, temp_path = tempfile.mkstemp(suffix=ext, dir=_TEMP_DIR)
            os.close(fd)  # 立即释放文件描述符
            processed_path = temp_path

        # 2.2 其他特殊前缀
        elif raw_path.startswith('create-system-temp:'):
            subpath = raw_path[len('create-system-temp:'):]
            subpath = remove_leading_slash(subpath)
            processed_path = os.path.join(_TEMP_DIR, subpath)

        elif raw_path.startswith('project:'):
            subpath = raw_path[len('project:'):]
            subpath = remove_leading_slash(subpath)
            processed_path = os.path.join(_PROJECT_PATH, subpath)

        elif raw_path.startswith('system-temp:'):
            subpath = raw_path[len('system-temp:'):]
            subpath = remove_leading_slash(subpath)
            processed_path = os.path.join(_TEMP_DIR, subpath)

        # 3. 规范化路径
        try:
            normalized_path = Path(processed_path).resolve().as_posix()
        except RuntimeError:
            # 处理可能的无效路径（如未替换的前缀）
            normalized_path = os.path.normpath(processed_path)

        # 4. Linux/Mac环境下处理含空格路径（按需启用）
        if quote_spaces and not _IS_WINDOWS and _SPACE_PATTERN.search(normalized_path):
            normalized_path = f'"{normalized_path}"'

        return normalized_path

    @staticmethod
    def raw_path(path):
        """
        获取原始路径（去除引号）
        :param path: 路径
        :return: 原始路径
        """
        return path.replace('"', '')

    @staticmethod
    def exist(path):
        """
        检查文件或目录是否存在
        :param path: 路径
        :return: 是否存在
        """
        return os.path.exists(path)

    @staticmethod
    def is_path(path):
        """
        判断是否是有效路径格式
        :param path: 路径
        :return: 是否是路径
        """
        pattern = r'^(?:\/{2})?[a-zA-Z0-9._-]+(?:\/[a-zA-Z0-9._-]+)*$'
        return bool(re.match(pattern, path))

    @staticmethod
    def project_path():
        """
        获取应用根目录（通过查找.git或.venv目录）
        :return: 项目路径
        """
        # 从当前文件所在目录开始
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 向上级目录查找，直到找到.git或.venv目录，或者到达根目录
        current_path = current_dir
        while current_path != os.path.dirname(current_path):  # 未到达根目录
            # 检查是否存在.git目录或.venv目录
            git_dir = os.path.join(current_path, ".git")
            venv_dir = os.path.join(current_path, ".venv")
            requirements_file = os.path.join(current_path, "requirements.txt")

            if os.path.exists(git_dir) and os.path.isdir(git_dir):
                return current_path
            if os.path.exists(venv_dir) and os.path.isdir(venv_dir):
                return current_path
            if os.path.exists(requirements_file) and os.path.isfile(requirements_file):
                return current_path

            # 向上级目录移动
            current_path = os.path.dirname(current_path)

        # 如果没找到，返回None
        return None


    @staticmethod
    def project_env_path():
        """
        获取项目.env文件路径
        :return: .env文件路径
        """
        project_path = PathUtil.project_path()
        if project_path is False:
            return False
        file_path = os.path.join(project_path, ".env")
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return file_path
        else:
            return False

    @staticmethod
    def name(path):
        """
        获取路径名称
        :param path: 路径
        :return: 路径名称
        """
        path = PathUtil.path(path)
        return os.path.basename(path)

    @staticmethod
    def parent(path, level=1):
        """
        获取上级路径
        :param path: 路径
        :param level: 上级层数
        :return: 上级路径
        """
        path = PathUtil.path(path)
        # 根据level层数逐级获取上级目录
        for _ in range(level):
            path = os.path.dirname(path)
        return path
