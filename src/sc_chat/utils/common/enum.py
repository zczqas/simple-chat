from enum import Enum


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"

    def __str__(self):
        return self.value
