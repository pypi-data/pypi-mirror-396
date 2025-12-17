import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from build.lib.gou2tool.util import IdUtil


class Instance:
    """
    实例类，用于存储和管理容器中的实例信息
    """

    # 实例编码
    id: str

    # 实例名称
    name: None

    # 命名空间
    namespace: Optional[str]

    # 是否初始化
    init: bool

    # 容器类
    concrete: Any

    # 类
    class_name: str

    # 注解
    annotations: List[Any]

    # 引用
    usages: List[Any]

    # 实例的路径
    path: str

    # 实例
    instance: Any

    # 代理
    proxy: Any

    # 接口
    interfaces: List[Any]  # ReflectionClass[] in PHP

    # 标签
    tags: List[str]

    # 父类
    father_class: Any  # ReflectionClass in PHP

    # 类型
    type: str

    # 实际入参
    vars: List[Any]

    # 入参
    params: List[Any]

    # 构造函数
    construct: Optional[List[Any]]

    # 是否每次创建新的实例
    new_instance: bool

    # 调用次数
    call_count: int

    # 创建时间
    create_time: str

    # 修改时间
    update_time: str

    # 调用时间
    call_time: str

    # 实例的备注
    remarks: Optional[str]

    # 父级实例
    parent_instance: Any

    def __init__(self):
        """
        初始化实例
        """
        self.id = IdUtil.simple_uuid()
        self.name = ""
        self.namespace = None
        self.init = False
        self.concrete = None
        self.class_name = ""
        self.annotations = []
        self.usages = []
        self.path = ""
        self.instance = None
        self.proxy = None
        self.interfaces = []
        self.tags = []
        self.father_class = None
        self.type = ""
        self.vars = []
        self.params = []
        self.construct = None
        self.new_instance = False
        self.call_count = 0
        self.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.call_time = ""
        self.remarks = None
        self.parent_instance = None
