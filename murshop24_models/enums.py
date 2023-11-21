import enum


class ProductUnitCountType(enum.StrEnum):
    MILLIGRAM = "MILLIGRAM"
    PIECE = "PIECE"


class OrderStatus(enum.StrEnum):
    PAYMENT_WAITING = "PAYMENT_WAITING"
    PAYMENT_CHECKING = "PAYMENT_CHECKING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
