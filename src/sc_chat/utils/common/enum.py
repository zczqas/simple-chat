from enum import Enum


class UserRoleEnum(Enum):
    USER = "user"
    ADMIN = "admin"

    def __str__(self):
        return self.value
