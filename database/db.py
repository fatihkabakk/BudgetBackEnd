from core.logging import Logger
from functools import wraps
import sqlite3


logger = Logger(__file__, 'Database.log')


def to_dict(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            data = func(*args, **kwargs)
            if isinstance(data, (list, tuple)):
                return [dict(**i) for i in data]
            elif data:
                return dict(**data)
        except Exception:
            raise

    return wrapper


def return_success(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
            return True
        except Exception:
            logger.critical(f"Exception In {func.__qualname__}", exc_info=True)
            return False

    return wrapper


class sql:
    def __init__(self, db_name="./database.db") -> None:
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    @logger.log
    @return_success
    def add(self, table, **kwargs) -> bool:
        print("Kwargs items:", [i for i in kwargs])
        cols = ", ".join([k for k, _ in kwargs.items()])
        vals = [v for _, v in kwargs.items()]
        query = f"INSERT INTO {table} ({cols}) VALUES ({', '.join(['?'] * len(kwargs))})"
        print("\n\n\n\nQUERY:", query)
        self.cursor.execute(query, vals)

    @logger.log
    @return_success
    def update(self, id, table, **kwargs) -> bool:
        print(dict(**kwargs))
        args = [f"{i}='{kwargs[i]}'" for i in kwargs]
        query = f"UPDATE {table} SET {', '.join(args)} WHERE id=?"
        self.cursor.execute(query, (id,))

    @logger.log
    @return_success
    def delete(self, id, table) -> bool:
        query = f"DELETE FROM {table} WHERE id=?"
        self.cursor.execute(query, (id,))

    @logger.log
    @to_dict
    def get(self, name, table, filter=None) -> object:
        query = f"SELECT * FROM {table} WHERE name=?"
        if filter:
            query += f"AND {filter}"
        self.cursor.execute(query, (name,))
        return self.cursor.fetchone()

    @logger.log
    @to_dict
    def get_by_id(self, id, table, filter=None) -> dict:
        query = f"SELECT * FROM {table} WHERE id=?"
        if filter:
            query += f"AND {filter}"
        self.cursor.execute(query, (id,))
        return self.cursor.fetchone()

    @logger.log
    @to_dict
    def get_column_names(self, table: str) -> list:
        query = f"PRAGMA table_info({table})"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    @logger.log
    @to_dict
    def get_all(self, table: str, filter: str = None) -> list:
        query = f"SELECT * FROM {table}"
        if filter:
            query += f" WHERE {filter}"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    @logger.log
    def close(self) -> bool:
        try:
            self.__exit__(None, None, None)
            return True
        except Exception:
            return False

    def __enter__(self) -> "sql":
        return self, self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()


def create_table_and_seed():
    with sql() as db:
        db.cursor.execute("DROP TABLE IF EXISTS players")
        db.cursor.execute(
            "CREATE TABLE IF NOT EXISTS players (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
        db.cursor.execute("INSERT INTO players (name) VALUES (?), (?), (?), (?)",
                          ("fatih", "emre", "yavuz", "ahmet"))


def main():
    with sql() as db:
        # create_table_and_seed()
        db.cursor.execute("SELECT * FROM sqlite_schema")
        db.cursor.fetchone()
        # print(dict(**db.cursor.fetchone()))
        print(db.get("fatih", "players"))
        print(db.get("emre", "players", "id=2"))
        print(db.get_all("players"))
        print([i["name"] for i in db.get_column_names("players")])
        print(db.update(1, "players", name="klinz"))
        print(db.get_by_id(1, "players"))
        print(db.delete(4, "players"))
        print(db.get_all("players"))


def test():
    with sql() as (db, cursor):
        print(db, cursor)


if __name__ == '__main__':
    test()
