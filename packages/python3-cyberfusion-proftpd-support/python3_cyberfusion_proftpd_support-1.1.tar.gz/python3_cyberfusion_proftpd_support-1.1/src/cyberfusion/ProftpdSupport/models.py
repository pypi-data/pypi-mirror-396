import datetime
from dataclasses import dataclass


@dataclass
class User:
    id: int
    username: str
    password: str
    uid: int
    gid: int
    home_directory: str
    shell_path: str
    created_at: datetime.datetime
