class DBTemplateUtil:
    _connection = None

    @classmethod
    def get_connectio(cls, connection=None):
        if connection is None and cls._connection is None:
            import mysql.connector
            from . import EnvUtil, PathUtil
            if PathUtil.project_env_path() and EnvUtil.has_group("DATABASE"):
                connection = mysql.connector.connect(
                    host=EnvUtil.get('HOSTNAME', 'localhost', 'DATABASE'),
                    database=EnvUtil.get('DATABASE', '', 'DATABASE'),
                    user=EnvUtil.get('USERNAME', '', 'DATABASE'),
                    password=EnvUtil.get('PASSWORD', '', 'DATABASE'),
                    port=EnvUtil.get('HOSTPORT', 3306, 'DATABASE')
                )
                cls.set_connectio(connection)
            else:
                raise Exception('请先设置数据库连接')
        return connection or cls._connection

    @classmethod
    def set_connectio(cls, connection=None):
        cls._connection = connection

    @classmethod
    def query_for_one(cls, sql, params=None, connection=None):
        """
        执行SQL查询并返回单个结果的字典格式

        Args:
            sql (str): SQL查询语句
            connection: 数据库连接对象
            params (tuple|dict|None): SQL参数，支持元组或字典格式

        Returns:
            dict|None: 查询结果的字典表示，如果没有结果则返回None
        """
        connection = cls.get_connectio(connection)
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

    @classmethod
    def query_for_list(cls, sql, params=None, connection=None):
        """
        执行SQL查询并返回所有结果的字典列表格式

        Args:
            sql (str): SQL查询语句
            params (tuple|dict|None): SQL参数，支持元组或字典格式
            connection: 数据库连接对象

        Returns:
            list: 查询结果的字典列表，每个元素是一行数据的字典表示
        """
        connection = cls.get_connectio(connection)
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

    @classmethod
    def execute(cls, sql, params=None, connection=None):
        """
        执行单条SQL增删改操作

        Args:
            sql (str): SQL语句
            params (tuple|dict|None): SQL参数，支持元组或字典格式
            connection: 数据库连接对象

        Returns:
            int: 受影响的行数
        """
        connection = cls.get_connectio(connection)
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

    @classmethod
    def execute_batch(cls, statements, batch_size=1000, connection=None):
        """
        批量执行多条SQL语句（支持分批处理）

        Args:
            statements (list): SQL语句列表
            batch_size (int): 每批处理的语句数量
            connection: 数据库连接对象

        Returns:
            int: 受影响的行数总计
        """
        if not statements:
            return 0

        connection = cls.get_connectio(connection)
        cursor = connection.cursor(dictionary=True)
        total_rowcount = 0

        try:
            # 按批次处理SQL语句
            for i in range(0, len(statements), batch_size):
                batch_statements = statements[i:i + batch_size]

                # 执行当前批次的所有语句
                for statement in batch_statements:
                    if isinstance(statement, tuple):
                        sql, params = statement
                        cursor.execute(sql, params)
                    else:
                        cursor.execute(statement)

                    total_rowcount += cursor.rowcount

                # 每批次提交一次事务
                connection.commit()

            return total_rowcount
        except Exception as e:
            connection.rollback()
            print(f"批量执行出错: {e}")
            return 0
        finally:
            cursor.close()
