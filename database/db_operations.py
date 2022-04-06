from sqlite_context import SqliteContext
from caching import cache, del_from_cache


@cache
def get_user_by_username(username: str):
    query = "SELECT * FROM users WHERE username = ?"

    with SqliteContext() as cursor:
        cursor.execute(query, (username,))
        user = cursor.fetchone()

    return user


@del_from_cache('get_user')
def register_user(username, password):
    query = "INSERT INTO users(username, password) VALUES(?, ?)"

    with SqliteContext() as cursor:
        cursor.execute(query, (username, password))
