from enum import Enum
from typing import Any


class RoleTypes(Enum):
    SuperUser = 'SuperUser'
    Admin = 'Admin'
    Staff = 'Staff'
    DeliveryBoy = 'DeliveryBoy'
    Customer = 'Customer'

    @classmethod
    def choices(cls) -> list[Any]:
        return [(key.value, key.name) for key in cls]
