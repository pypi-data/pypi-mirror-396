from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from tp_shared.routing_service.types.routing_types import Latitude, Longitude


class BaseRoutePoint(BaseModel):
    """
    Базовая схема точки маршрута
    """

    lat: Latitude = Field(ge=-90, le=90, description="Широта")
    lon: Longitude = Field(ge=-180, le=180, description="Долгота")
    order_sequence: int = Field(ge=0, description="Порядок в маршруте")


class RoutePointCreate(BaseRoutePoint):
    """
    Схема создания точки маршрута
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Window(BaseModel):
    window_from: datetime | None = Field(None, ge=0, description="Порядок в маршруте")
    window_to: datetime | None = Field(None, ge=0, description="Порядок в маршруте")


class CPRoutingOptimizeRequest(BaseModel):
    """Схема запроса на оптимизацию маршрута"""

    points: list[RoutePointCreate] = Field(
        min_length=2, max_length=15, description="Точки маршрута"
    )
    cargo_weight_kg: Decimal = Field(
        None, ge=0, description="Вес груза в килограммах (опционально)"
    )
    avoid_tolls: bool = Field(False, description="Избегать платных дорог")
    window: Window | None = Field(None, description="Временные окна")
