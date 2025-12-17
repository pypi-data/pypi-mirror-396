from typing import List, Dict, Any, Callable
import copy


class TreeUtil:
    """
    树结构工具类
    """

    @staticmethod
    def list_to_tree(list_data: List[Dict[str, Any]], config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        数组转树结构
        :param list_data: 原始列表数据
        :param config: 配置参数
        :return: 树结构数据
        """
        if config is None:
            config = {}

        # 初始化参数
        config.setdefault("id", "id")
        config.setdefault("parent_id", "parent_id")
        config.setdefault("children", "children")

        # 新建映射关系
        map_dict = {}
        filtered_list = []

        for item in list_data:
            # 跳过开头的上级节点
            if "level" in config and "init_level" in config and config.get("level") in item:
                if item[config["level"]] < config["init_level"]:
                    continue
            map_dict[item[config["id"]]] = item
            filtered_list.append(item)

        # 树数据
        tree = []
        for item in filtered_list:
            # 跳过开头的上级节点
            if "level" in config and "init_level" in config and config.get("level") in item:
                if item[config["level"]] < config["init_level"]:
                    continue

            # 获取上级节点
            parent_id = None
            if item[config["parent_id"]] in map_dict:
                parent_id = item[config["parent_id"]]
            else:
                # 通过完整id字段 查找上级节点 补充缺省上级数据
                if "full_id" in config and config["full_id"] in item:
                    ids = item[config["full_id"]].split(",")
                    for id_val in ids:
                        if item[config["id"]] != id_val and id_val in map_dict:
                            parent_id = id_val

            # 判断上级节点是否存在 不存在则添加到顶级节点
            if parent_id is not None:
                # 添加到子节点
                if config["children"] not in map_dict[parent_id]:
                    map_dict[parent_id][config["children"]] = []
                map_dict[parent_id][config["children"]].append(item)
            else:
                tree.append(item)

        def recursion(data, next_func, node):
            result = []
            for item in data:
                new_item = copy.deepcopy(item)
                if "level" in config:
                    new_item[config["level"]] = node["level"]

                if config["children"] in new_item:
                    if "level" in config and "max_level" in config:
                        if node["level"] + 1 > config["max_level"]:
                            del new_item[config["children"]]
                        else:
                            new_item[config["children"]] = next_func(new_item[config["children"]], next_func)
                    else:
                        new_item[config["children"]] = next_func(new_item[config["children"]], next_func)
                result.append(new_item)
            return result

        return TreeUtil.recursion(tree, recursion)

    @staticmethod
    def tree_to_list(tree: List[Dict[str, Any]], config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        树结构转数组
        :param tree: 树结构数据
        :param config: 配置参数
        :return: 列表数据
        """
        if config is None:
            config = {}

        config.setdefault("children", "children")
        config.setdefault("unset_children", True)

        def list_handle(tree_data, conf, handler):
            result = []
            for item in tree_data:
                new_item = copy.deepcopy(item)
                children = None
                if conf["children"] in new_item:
                    children = new_item[conf["children"]]
                    if conf.get("unset_children", True):
                        del new_item[conf["children"]]
                else:
                    children = None

                result.append(new_item)
                if isinstance(children, list):
                    result.extend(handler(children, conf, handler))
            return result

        return list_handle(tree, config, list_handle)

    @staticmethod
    def get_max_depth(tree: List[Dict[str, Any]], config: Dict[str, Any] = None) -> int:
        """
        获取树节点的最大深度
        :param tree: 树结构数据
        :param config: 配置参数
        :return: 最大深度
        """
        if config is None:
            config = {}

        config.setdefault("id", "id")
        config.setdefault("children", "children")

        max_depth = 0

        def callback(item, node):
            nonlocal max_depth
            if node['level'] + 1 > max_depth:
                max_depth = node['level'] + 1

        TreeUtil.recursion_each(tree, callback, config)
        return max_depth

    @staticmethod
    def recursion(param_or_tree: List[Dict[str, Any]], main_next: Callable,
                   node: Dict[str, Any] = None) -> Any:
        """
        递归处理树形数据的核心方法
        :param param_or_tree: 待处理的数据
        :param main_next: 处理函数
        :param node: 节点信息
        :return: 处理后的结果
        """
        if node is None:
            node = {"level": 0, "top": True, "parent": None, "parents": []}

        def next_func(param_or_tree_inner, parent):
            new_node = {
                "level": node["level"] + 1,
                "top": False,
                "parent": parent,
                "parents": node["parents"] + [parent] if parent else []
            }
            return TreeUtil.recursion(param_or_tree_inner, main_next, new_node)

        return main_next(param_or_tree, next_func, node)

    @staticmethod
    def recursion_each(tree: List[Dict[str, Any]], func: Callable,
                       config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        遍历树形结构中的每个节点并执行回调函数
        :param tree: 树形结构数据
        :param func: 回调函数
        :param config: 配置参数
        :return: 处理后的树
        """
        if config is None:
            config = {}

        config.setdefault("children", "children")

        def tree_handle(tree_data, handler, node=None):
            if node is None:
                node = {"level": 0, "top": True, "parent": None, "parents": []}

            for item in tree_data:
                func(item, node)
                if config["children"] in item and isinstance(item[config["children"]], list):
                    handler(
                        item[config["children"]],
                        handler,
                        {
                            "parent": item,
                            "parents": node["parents"] + [item],
                            "level": node["level"] + 1,
                            "top": False,
                        }
                    )

        tree_handle(tree, tree_handle)
        return tree
