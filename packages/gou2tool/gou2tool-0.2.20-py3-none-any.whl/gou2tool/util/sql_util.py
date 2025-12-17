import json

class SQLUtil:
    """SQL语句生成工具类"""

    @staticmethod
    def escape_string(val):
        """
        转义SQL字符串中的特殊字符

        Args:
            val: 要转义的字符串

        Returns:
            转义后的字符串
        """
        if isinstance(val, str):
            # 转义单引号
            return val.replace("'", "''")
        return val

    @staticmethod
    def format_value(val):
        """
        格式化值为SQL字符串

        Args:
            val: 要格式化的值

        Returns:
            格式化后的SQL值字符串
        """
        if val is None:
            return "NULL"
        elif isinstance(val, str):
            # 转义字符串并加引号
            escaped_val = SQLUtil.escape_string(val)
            return f"'{escaped_val}'"
        elif isinstance(val, (list, tuple)):
            # 数组转为逗号分隔的字符串
            escaped_val = SQLUtil.escape_string(','.join(map(str, val)))
            return f"'{escaped_val}'"
        elif isinstance(val, dict):
            # 字典转为JSON字符串
            escaped_val = SQLUtil.escape_string(json.dumps(val, ensure_ascii=False))
            return f"'{escaped_val}'"
        else:
            return str(val)

    @staticmethod
    def insert(table: str, data: dict, returning: str = None) -> str:
        """
        生成INSERT SQL语句

        Args:
            table: 表名
            data: 要插入的数据字典 {列名: 值}
            returning: 返回指定列的值（可选）

        Returns:
            INSERT SQL语句
        """
        columns = ', '.join(data.keys())

        # 直接使用值而不是占位符
        values = []
        for val in data.values():
            values.append(SQLUtil.format_value(val))

        placeholders = ', '.join(values)
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        if returning:
            sql += f" RETURNING {returning}"

        return sql

    @staticmethod
    def batch_insert(table: str, data_list: list) -> str:
        """
        生成批量INSERT SQL语句

        Args:
            table: 表名
            data_list: 要插入的数据列表 [{列名: 值}, ...]

        Returns:
            批量INSERT SQL语句
        """
        if not data_list:
            return ""

        columns = ', '.join(data_list[0].keys())
        sql = f"INSERT INTO {table} ({columns}) VALUES "

        # 构建所有值的列表
        value_groups = []
        for data in data_list:
            values = []
            for val in data.values():
                values.append(SQLUtil.format_value(val))
            value_groups.append(f"({', '.join(values)})")

        sql += ', '.join(value_groups)
        return sql

    @staticmethod
    def update(table: str, data: dict, where: dict = None, where_clause: str = None) -> str:
        """
        生成UPDATE SQL语句

        Args:
            table: 表名
            data: 要更新的数据字典 {列名: 值}
            where: WHERE条件字典 {列名: 值}
            where_clause: 自定义WHERE子句（可选）

        Returns:
            UPDATE SQL语句
        """
        if not data:
            raise ValueError("更新数据不能为空")

        # 直接使用值而不是占位符
        set_parts = []
        for col, val in data.items():
            formatted_val = SQLUtil.format_value(val)
            set_parts.append(f"`{col}` = {formatted_val}")

        set_clause = ', '.join(set_parts)
        sql = f"UPDATE `{table}` SET {set_clause}"

        # 处理WHERE条件
        if where_clause:
            sql += f" WHERE {where_clause}"
        elif where:
            where_parts = []
            for col, val in where.items():
                if val is None:
                    where_parts.append(f"`{col}` IS NULL")
                elif isinstance(val, dict):
                    # 支持操作符字典 {"=": 1, ">": 5, "LIKE": "%test%", "IN": [1,2,3]}
                    for op, op_val in val.items():
                        if op.upper() == "IN" and isinstance(op_val, (list, tuple)):
                            in_vals = [SQLUtil.format_value(v) for v in op_val]
                            where_parts.append(f"`{col}` IN ({', '.join(in_vals)})")
                        if op.upper() == "NOT IN" and isinstance(op_val, (list, tuple)):
                            in_vals = [SQLUtil.format_value(v) for v in op_val]
                            where_parts.append(f"`{col}` NOT IN ({', '.join(in_vals)})")
                        elif op.upper() in ["LIKE", "=", "!=", ">", "<", ">=", "<="]:
                            formatted_val = SQLUtil.format_value(op_val)
                            where_parts.append(f"`{col}` {op.upper()} {formatted_val}")
                        else:
                            formatted_val = SQLUtil.format_value(op_val)
                            where_parts.append(f"`{col}` {op} {formatted_val}")
                else:
                    formatted_val = SQLUtil.format_value(val)
                    where_parts.append(f"`{col}` = {formatted_val}")
            if where_parts:
                sql += " WHERE " + " AND ".join(where_parts)

        return sql

    @staticmethod
    def delete(table: str, where: dict = None, where_clause: str = None) -> str:
        """
        生成DELETE SQL语句

        Args:
            table: 表名
            where: WHERE条件字典 {列名: 值}
            where_clause: 自定义WHERE子句（可选）

        Returns:
            DELETE SQL语句
        """
        sql = f"DELETE FROM {table}"

        # 处理WHERE条件
        if where_clause:
            sql += f" WHERE {where_clause}"
        elif where:
            where_parts = []
            for col, val in where.items():
                if val is None:
                    where_parts.append(f"{col} IS NULL")
                elif isinstance(val, dict):
                    # 支持操作符字典 {"=": 1, ">": 5, "LIKE": "%test%", "IN": [1,2,3]}
                    for op, op_val in val.items():
                        if op.upper() == "IN" and isinstance(op_val, (list, tuple)):
                            in_vals = [SQLUtil.format_value(v) for v in op_val]
                            where_parts.append(f"{col} IN ({', '.join(in_vals)})")
                        elif op.upper() in ["LIKE", "=", "!=", ">", "<", ">=", "<="]:
                            formatted_val = SQLUtil.format_value(op_val)
                            where_parts.append(f"{col} {op.upper()} {formatted_val}")
                        else:
                            formatted_val = SQLUtil.format_value(op_val)
                            where_parts.append(f"{col} {op} {formatted_val}")
                else:
                    formatted_val = SQLUtil.format_value(val)
                    where_parts.append(f"{col} = {formatted_val}")
            if where_parts:
                sql += " WHERE " + " AND ".join(where_parts)
        else:
            # 防止意外删除所有数据
            raise ValueError("删除操作必须提供WHERE条件")

        return sql
