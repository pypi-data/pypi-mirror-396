import os
import re
import tempfile
import uuid
from pathlib import Path


class PathUtil:
    """路径工具类"""

    @staticmethod
    def path(*paths):
        """
        构建路径
        :param paths: 路径组件
        :return: 完整路径
        """
        # 连接路径组件
        path = "/".join(paths)

        # 处理特殊前缀
        if path.startswith('project:'):
            path = path.replace("project:", PathUtil.project_path(), 1)
        elif path.startswith('goutool:'):
            path = path.replace("goutool:", PathUtil.goutool_path(), 1)
        elif path.startswith('gou2tool:'):
            path = path.replace("gou2tool:", PathUtil.goutool_path(), 1)
        elif path.startswith('system-temp:'):
            path = path.replace("system-temp:", tempfile.gettempdir(), 1)
        elif path.startswith('create-system-temp:'):
            temp_dir = tempfile.gettempdir()
            filename = path.replace("create-system-temp:", "")
            path = os.path.join(temp_dir, filename)
        elif path.startswith('create-system-temp-file:*'):
            temp_dir = tempfile.gettempdir()
            if path.startswith('create-system-temp-file:*.*'):
                ext = path.replace("create-system-temp-file:*.*", ".", 1)
            elif path.startswith('create-system-temp-file:*'):
                ext = ".tmp"
            else:
                ext = ""
            filename = str(uuid.uuid4()) + ext
            path = os.path.join(temp_dir, filename)
        elif path.startswith('vendor:'):
            path = path.replace("vendor:", os.path.join(PathUtil.project_path(), "vendor"), 1)

        # 规范化路径分隔符
        lists = [part for part in re.split(r'([/\\]+)', path) if part]

        # Linux环境下处理包含空格的路径
        if os.name != 'nt':  # 非Windows系统
            parts = re.split(r'([\\/]+)', path)
            for i, part in enumerate(parts):
                if re.search(r'\s', part) and not (part.startswith('"') and part.endswith('"')):
                    parts[i] = f'"{part}"'
            path = "".join(parts)

        return "".join(lists)

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
        获取应用根目录
        :return: 项目路径
        """
        # 这里需要根据实际项目结构调整
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project = os.path.dirname(current_dir)  # 根据实际情况调整层级

        project_file = os.path.join(project, "composer.json")
        project_vendor = os.path.join(project, "vendor")
        goutool_file = os.path.join(project, "vendor", "wl4837", "goutool", "composer.json")

        if (os.path.exists(project_file) and os.path.isfile(project_file) and
                os.path.exists(project_vendor) and os.path.isdir(project_vendor) and
                os.path.exists(goutool_file) and os.path.isfile(goutool_file)):
            return project
        else:
            return PathUtil.goutool_path()

    @staticmethod
    def goutool_path():
        """
        获取框架目录
        :return: 框架路径
        """
        path = PathUtil.parent(os.path.abspath(__file__), 6)
        file_path = os.path.join(path, "setup.py")
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return path
        return False

    @staticmethod
    def project_composer_path():
        """
        获取项目composer.json路径
        :return: composer.json路径
        """
        project_path = PathUtil.project_path()
        if project_path is False:
            return False
        file_path = os.path.join(project_path, "composer.json")
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return file_path
        else:
            return False

    @staticmethod
    def project_package_path():
        """
        获取项目package.json路径
        :return: package.json路径
        """
        project_path = PathUtil.project_path()
        if project_path is False:
            return False
        file_path = os.path.join(project_path, "package.json")
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return file_path
        else:
            return False

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
    def goutool_composer_path():
        """
        获取框架composer.json路径
        :return: composer.json路径
        """
        goutool_path = PathUtil.goutool_path()
        if goutool_path is False:
            return False
        file_path = os.path.join(goutool_path, "composer.json")
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
