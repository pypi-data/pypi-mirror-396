import configparser
from pathlib import Path


class EnvUtil:

    @staticmethod
    def get(name, default=None, group='DEFAULT', env_file_path=None):
        config = configparser.ConfigParser()

        with open(env_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip().startswith('['):
            content = '[DEFAULT]\n' + content

        config.read_string(content)

        return config.get(group, name, fallback=default)
