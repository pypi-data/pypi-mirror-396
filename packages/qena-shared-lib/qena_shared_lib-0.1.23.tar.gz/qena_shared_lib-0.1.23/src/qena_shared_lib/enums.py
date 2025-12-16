from enum import Enum

__all__ = ["ServiceType"]


class ServiceType(Enum):
    HTTP = 0
    RABBIT_MQ = 1
