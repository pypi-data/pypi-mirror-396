from gou2tool.core.instance import Instance
from gou2tool.util import StrUtil


class Container:
    """
    容器化管理实例类
    设计模式为单例
    参考的Thinkphp 和 Spring boot 的 Bean合
    """

    _container = None

    _instances = {}

    _init_binds = []

    def __init__(self):
        _init_binds = []

    @classmethod
    def get_container(cls):
        """获取容器实例（单例模式）"""
        if cls._container is None:
            cls._container = cls.__new__(cls)
            # 初始化绑定
            for init_bind in cls._init_binds:
                cls.set(init_bind)
        return cls._container

    @classmethod
    def set_container(cls, instance):
        """设置容器实例"""
        cls._container = instance

    @classmethod
    def set(cls, options=None):
        if options is None:
            options = {}
        name = options.get("name", None)
        concrete = options.get("concrete")
        var_list = options.get("var_list", [])
        remarks = options.get("remarks")
        init = options.get("init", True)
        cover = options.get("cover", False)
        new_instance = options.get("newInstance", False)
        construct = options.get("construct")
        parent_instance = options.get("parentInstance")
        if cls.has(name):
            # 有没有定义自己名称的优先
            instance = cls.get(name)
        elif cls.has_init_instance(concrete):
            # 有没有预加载的优先加载预加载
            instance = cls.get_init_instance(concrete)
        else:
            # 保底初始化
            instance = Instance()
        instance.name = name
        instance.vars = var_list
        instance.remarks = remarks
        instance.init = init
        instance.new_instance = new_instance
        instance.construct = construct
        instance.parent_instance = parent_instance
        instance.concrete = concrete
        cls.get_container()._instances[instance.id] = instance
        return instance

    @classmethod
    def get(cls, name):
        return cls.get_name(name)

    @classmethod
    def get_name(cls, name):
        result = None
        instances = cls.get_container()._instances
        for instance in instances.values():
            if StrUtil.equals(StrUtil.lower_case(instance.name), StrUtil.lower_case(name)):
                result = instance.proxy
        if result is not None:
            return result
        raise RuntimeError("实例不存在")

    @classmethod
    def has(cls, name):
        if StrUtil.has_empty(name):
            return False
        instances = cls.get_container()._instances
        for instance in instances.values():
            if StrUtil.equals(StrUtil.lower_case(instance.name), StrUtil.lower_case(name)):
                return True
        return False

    @classmethod
    def has_init_instance(cls, concrete):
        return False

    @classmethod
    def get_init_instance(cls, concrete):
        return False
