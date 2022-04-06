import sqlite3
import os


class SqliteContext:
    def __enter__(self):
        self.connection = sqlite3.connect('data.db')
        self.cursor = self.connection.cursor(dictionary=True)
        self.cursor.connection = self.connection
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()


if __name__ == '__main__':
    with SqliteContext() as cursor:
        print(cursor.connection)
