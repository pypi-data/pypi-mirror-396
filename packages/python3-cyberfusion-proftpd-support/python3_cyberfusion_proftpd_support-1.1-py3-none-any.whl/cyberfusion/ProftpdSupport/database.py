import sqlite3

from cyberfusion.ProftpdSupport.settings import settings


def get_database_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(settings.database_path, isolation_level=None)

    connection.row_factory = sqlite3.Row  # Allow named access to columns

    return connection
