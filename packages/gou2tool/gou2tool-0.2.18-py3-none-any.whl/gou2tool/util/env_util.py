import configparser

from . import PathUtil


class EnvUtil:

    @staticmethod
    def get(name, default=None, group='DEFAULT', env_file_path=None):
        if env_file_path is None:
            env_file_path = PathUtil.project_env_path()

        config = configparser.ConfigParser()

        with open(env_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip().startswith('['):
            content = '[DEFAULT]\n' + content

        config.read_string(content)

        return config.get(group, name, fallback=default)

    @staticmethod
    def has(name, group='DEFAULT', env_file_path=None):
        """
        检查环境变量是否存在

        Args:
            name: 环境变量名称
            group: 配置组名，默认为'DEFAULT'
            env_file_path: 环境文件路径，默认使用项目环境路径

        Returns:
            bool: 存在返回True，否则返回False
        """
        if env_file_path is None:
            env_file_path = PathUtil.project_env_path()

        config = configparser.ConfigParser()

        with open(env_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip().startswith('['):
            content = '[DEFAULT]\n' + content

        config.read_string(content)

        return config.has_option(group, name)

    @staticmethod
    def has_group(group, env_file_path=None):
        """
        检查环境配置文件中是否存在指定组

        Args:
            group: 配置组名
            env_file_path: 环境文件路径，默认使用项目环境路径

        Returns:
            bool: 组存在返回True，否则返回False
        """
        if env_file_path is None:
            env_file_path = PathUtil.project_env_path()

        config = configparser.ConfigParser()

        with open(env_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip().startswith('['):
            content = '[DEFAULT]\n' + content

        config.read_string(content)

        return group in config.sections() or (group == 'DEFAULT' and len(config.defaults()) > 0)
