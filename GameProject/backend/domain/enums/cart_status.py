from enum import Enum


class CartStatusEnum(str, Enum):

    ACTIVE = 'ACTIVE'
    ORDERED = 'ORDERED'
    CANCELED = 'CANCELED'
    EXPIRED = 'EXPIRED'
