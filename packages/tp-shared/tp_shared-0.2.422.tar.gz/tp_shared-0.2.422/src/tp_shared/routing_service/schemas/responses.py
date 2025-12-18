from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from tp_shared.routing_service.schemas.base import RoutePlanBase
from tp_shared.routing_service.types.routing_types import (
    DistanceKm,
    DurationMinutes,
    RouteOptimizationType,
    RouteStatus,
)


class CPRoutingOptimizeResponse(RoutePlanBase):
    """Схема ответа оптимизации маршрута"""

    status: RouteStatus = Field(
        RouteStatus.DRAFT, description="Статус маршрута. По умолчанию - DRAFT"
    )
    optimization_mode: RouteOptimizationType = Field(description="Тип оптимизации")
    total_distance_km: DistanceKm = Field(description="Расстояние в км")
    total_duration_minutes: DurationMinutes = Field(
        description="Общее время в пути (в минутах)"
    )
    fuel_consumption_liters: float = Field(description="Расход топлива")
    fuel_cost: float = Field(description="Стоимость топлива")
    driver_salary_cost: float = Field(description="Зарплата водителя")
    total_route_cost: float = Field(description="Общая стоимость")
    recommended_price: float = Field(description="Рекомендованная стоимост маршрута")
    margin_percent: float = Field(description="Общее время в пути (в минутах)")
    polyline: str = Field(description="Строка polyline")

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)


class CPRoutingResponse(RoutePlanBase):
    """Схема ответа плана маршрута"""

    status: RouteStatus = Field(description="Статус плана маршрута")
    total_distance_km: DistanceKm = Field(description="Расстояние в км")
    total_duration_minutes: DurationMinutes = Field(
        description="Общее время в пути (в минутах)"
    )
    tracking_token: str | None = Field(
        None, description="URL для отслеживания маршрута"
    )
    polyline: str = Field(description="Строка polyline")
    created_at: datetime = Field(description="Дата создания плана маршрута")
    updated_at: datetime = Field(description="Дата обновления плана маршрута")
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)


class CPRoutingResponseList(BaseModel):
    routes: list[CPRoutingResponse] | None = Field(None, description="Список маршрутов")
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)


class CPRoutingOptimizeResponseList(BaseModel):
    routes: list[CPRoutingOptimizeResponse] | None = Field(
        None, description="Список маршрутов с экономикой"
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
