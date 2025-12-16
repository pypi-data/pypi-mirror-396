from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gou2tool",
    version="0.2.15",
    author="kingood",
    author_email="wl4837@qq.com",
    description="🐶 Python工具类库 更加快速的开发项目 便捷优雅的使用类库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/kingood/gou2tool",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[],
    extras_require={
        "dev": ["pytest>=6.0", "twine>=3.0"],
    },
)