import datetime
import os
from typing import List

from cyberfusion.ProftpdSupport.database import get_database_connection
from cyberfusion.ProftpdSupport.models import User
from cyberfusion.ProftpdSupport.settings import settings

PATH_SHELL = os.path.join(os.path.sep, "bin", "false")


def get_expire_users_ids() -> List[int]:
    connection = get_database_connection()

    cursor = connection.cursor()

    cursor.execute(
        f"SELECT * FROM `users` WHERE `created_at` < datetime('now', '-{settings.user_expire_hours} hours')"
    )

    return [row["id"] for row in cursor.fetchall()]


def get_user(username: str) -> User:
    connection = get_database_connection()

    cursor = connection.cursor()

    user = cursor.execute(
        "SELECT `id`, `userid`, `passwd`, `uid`, `gid`,`homedir`, `shell`, `created_at` FROM `users` WHERE `userid` = ?",
        (username,),
    ).fetchone()

    return User(
        id=user["id"],
        username=user["userid"],
        password=user["passwd"],
        uid=user["uid"],
        gid=user["gid"],
        home_directory=user["homedir"],
        shell_path=user["shell"],
        created_at=datetime.datetime.strptime(user["created_at"], "%Y-%m-%d %H:%M:%S"),
    )


def delete_expire_users() -> None:
    expire_users_ids = get_expire_users_ids()

    connection = get_database_connection()

    cursor = connection.cursor()

    for id_ in expire_users_ids:
        cursor.execute("DELETE FROM `users` WHERE `id` = ?", (str(id_)))


def get_users_amount() -> int:
    connection = get_database_connection()

    cursor = connection.cursor()

    return cursor.execute("SELECT COUNT(*) FROM `users`").fetchone()[0]


def create_proftpd_user(
    *, username: str, password: str, uid: int, gid: int, home_directory: str
) -> User:
    connection = get_database_connection()

    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO `users`(`userid`, `passwd`, `uid`, `gid`, `homedir`, `shell`) VALUES(?, ?, ?, ?, ?, ?)",
        (
            username,
            password,
            uid,
            gid,
            home_directory,
            PATH_SHELL,
        ),
    )

    return get_user(username)
