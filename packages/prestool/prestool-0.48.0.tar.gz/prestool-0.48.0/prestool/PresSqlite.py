from .PresMySql import PresMySql
from contextlib import contextmanager
import sqlite3


class PresSqlite(PresMySql):
    def __init__(self):
        super().__init__()
        self.sqlite_path = ''

    @staticmethod
    def dict_factory(cursor, row):
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

    @contextmanager
    def conn_sql(self):
        super().conn_sql()
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = self.dict_factory
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            conn.commit()
            cursor.close()
            conn.close()