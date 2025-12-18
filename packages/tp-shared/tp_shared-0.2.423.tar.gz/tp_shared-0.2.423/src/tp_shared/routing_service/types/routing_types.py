from decimal import Decimal
from enum import Enum
from typing import NewType

DistanceKm = NewType("DistanceKm", Decimal)
DurationMinutes = NewType("DurationMinutes", int)
Latitude = NewType("Latitude", float)
Longitude = NewType("Longitude", float)


class RouteStatus(str, Enum):
    """
    Статусы маршрута
    DRAFT - черновик
    APPROVED - опубликован
    CANCELLED - отменен
    """

    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    CANCELLED = "CANCELLED"


class RouteOptimizationType(str, Enum):
    """
    Типы оптимизации маршрута
    WITHOUT_TOLLS - оптимизация без учета платных дорог
    WITH_TOLLS - оптимизация с учетом платных дорогй
    """

    WITHOUT_TOLLS = "WITHOUT_TOLLS"
    WITH_TOLLS = "WITH_TOLLS"
