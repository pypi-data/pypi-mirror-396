from .Utils import make_sql_str_util
import pymysql
from contextlib import contextmanager


class SqlStr:
    @staticmethod
    def select_sql_str(table, target=None, where=None, order=None, limit=None, select_in=None, between=None, like=None,
                       compare=None, select_not_in=None, is_not_null=None):
        return make_sql_str_util('select', table, select_target=target, where=where, order_by=order, limit=limit,
                                 select_in=select_in, between=between, like=like, compare=compare,
                                 select_not_in=select_not_in, is_not_null=is_not_null)

    @staticmethod
    def update_sql_str(table, target, where, select_in=None, between=None, like=None, compare=None, select_not_in=None,
                       is_not_null=None):
        return make_sql_str_util('update', table, update_target=target, where=where, select_in=select_in,
                                 between=between, like=like, compare=compare, select_not_in=select_not_in,
                                 is_not_null=is_not_null)

    @staticmethod
    def delete_sql_str(table, where, select_in=None, between=None, like=None, compare=None, select_not_in=None,
                       is_not_null=None):
        return make_sql_str_util('delete', table, where=where, select_in=select_in, between=between, like=like,
                                 compare=compare, select_not_in=select_not_in, is_not_null=is_not_null)

    @staticmethod
    def insert_sql_str(table, target):
        return make_sql_str_util('insert', table, insert_target=target)


class PresMySql(SqlStr):
    def __init__(self):
        self.mysql_host = ''
        self.mysql_port = 3306
        self.mysql_user = ''
        self.mysql_pwd = ''
        self.mysql_db_name = ''
        self.mysql_charset = 'utf8mb4'

    @contextmanager
    def conn_sql(self):
        conn = pymysql.connect(
            host=self.mysql_host, user=self.mysql_user, password=self.mysql_pwd,
            db=self.mysql_db_name, charset=self.mysql_charset, port=self.mysql_port)
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        try:
            yield cursor
        finally:
            conn.commit()
            cursor.close()
            conn.close()

    def exec_sql(self, sql_str, select=None):
        with self.conn_sql() as db:
            db.execute(sql_str)
            if select == 'all':
                return db.fetchall()
            elif select == 'one':
                return db.fetchone()

    # 执行插入语句
    def to_insert(self, table, target):
        return self.exec_sql(self.insert_sql_str(table, target))

    # 执行删除语句
    def to_delete(self, table, where, select_in=None, between=None, like=None, compare=None, select_not_in=None,
                  is_not_null=None):
        return self.exec_sql(
            self.delete_sql_str(table, where, select_in=select_in, between=between, like=like, compare=compare,
                                select_not_in=select_not_in, is_not_null=is_not_null))

    # 执行更新语句
    def to_update(self, table, target, where, select_in=None, between=None, like=None, compare=None, select_not_in=None,
                  is_not_null=None):
        return self.exec_sql(
            self.update_sql_str(table, target, where, select_in=select_in, between=between, like=like, compare=compare,
                                select_not_in=select_not_in, is_not_null=is_not_null))

    # 查询符合条件的所有
    def to_query(self, table, target=None, where=None, order=None, limit=None, is_all=True, select_in=None,
                 between=None, like=None, compare=None, select_not_in=None, is_not_null=None):
        return self.exec_sql(
            self.select_sql_str(table, target, where, order, limit, select_in=select_in, between=between, like=like,
                                compare=compare, select_not_in=select_not_in, is_not_null=is_not_null),
            'all' if is_all else 'one')

    # 执行特殊查询
    def to_query_with_sql(self, sql_str, is_all=True):
        return self.exec_sql(sql_str, 'all' if is_all else 'one')
