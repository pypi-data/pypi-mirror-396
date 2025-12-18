import uuid

from pydantic import BaseModel, Field


class RoutePlanBase(BaseModel):
    """
    Базовая схема плана маршрута
    """

    route_plan_id: uuid.UUID | None = Field(None, description="ID плана маршрута")
    trip_id: uuid.UUID | None = Field(None, description="ID плана маршрута")
    vehicle_id: uuid.UUID | None = Field(None, description="id ТС")
    driver_id: uuid.UUID | None = Field(None, description="id водителя (опционально)")
    client_id: uuid.UUID | None = Field(None, description="id заказчика (опционально)")
