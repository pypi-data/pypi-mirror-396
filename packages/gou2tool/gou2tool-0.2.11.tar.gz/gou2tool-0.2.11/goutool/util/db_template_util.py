import re

class DBTemplateUtil:

    @staticmethod
    def query_for_one(sql, params=None, connection=None):
        """
        执行SQL查询并返回单个结果的字典格式

        Args:
            sql (str): SQL查询语句
            connection: 数据库连接对象
            params (tuple|dict|None): SQL参数，支持元组或字典格式

        Returns:
            dict|None: 查询结果的字典表示，如果没有结果则返回None
        """
        cursor = connection.cursor(dictionary=True)
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            return cursor.fetchone()
        except Exception as e:
            print(f"查询执行出错: {e}")
            return None
        finally:
            cursor.close()

    @staticmethod
    def query_for_list(sql, params=None, connection=None):
        """
        执行SQL查询并返回所有结果的字典列表格式

        Args:
            sql (str): SQL查询语句
            params (tuple|dict|None): SQL参数，支持元组或字典格式
            connection: 数据库连接对象

        Returns:
            list: 查询结果的字典列表，每个元素是一行数据的字典表示
        """
        cursor = connection.cursor(dictionary=True)
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"查询执行出错: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def execute(sql, params=None, connection=None):
        """
        执行单条SQL增删改操作

        Args:
            sql (str): SQL语句
            params (tuple|dict|None): SQL参数，支持元组或字典格式
            connection: 数据库连接对象

        Returns:
            int: 受影响的行数
        """
        cursor = connection.cursor(dictionary=True)
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            # 提交事务
            connection.commit()
            # 返回受影响的行数
            return cursor.rowcount
        except Exception as e:
            # 发生异常时回滚事务
            connection.rollback()
            print(f"执行出错: {e}")
            return 0
        finally:
            cursor.close()

    @staticmethod
    def execute_batch(sql, params_list=None, connection=None):
        """
        批量执行SQL增删改操作

        Args:
            sql (str): SQL语句模板
            params_list (list): 参数列表，每个元素是tuple或dict格式的参数
            connection: 数据库连接对象

        Returns:
            int: 受影响的行数总计
        """
        cursor = connection.cursor(dictionary=True)
        try:
            if params_list:
                # 批量执行带参数的SQL语句
                cursor.executemany(sql, params_list)
            else:
                # 单次执行不带参数的SQL语句
                cursor.execute(sql)

            # 提交事务
            connection.commit()
            # 返回受影响的行数
            return cursor.rowcount
        except Exception as e:
            # 发生异常时回滚事务
            connection.rollback()
            print(f"批量执行出错: {e}")
            return 0
        finally:
            cursor.close()
