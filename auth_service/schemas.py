from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# 📌 Схемы для дней маршрута
class ScheduleBase(BaseModel):
    day_number: int = Field(..., ge=1, description="Номер дня маршрута (начинается с 1)")
    activities: Optional[str] = Field(None, description="Описание событий на этот день")
    image: Optional[str] = Field(None, description="Ссылка на изображение")


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleResponse(ScheduleBase):
    id: int


# 📌 Схемы для маршрутов
class RouteBase(BaseModel):
    cities: List[str] = Field(..., description="Список основных городов или достопримечательностей")
    description: Optional[str] = Field(None, description="Описание маршрута")


class RouteCreate(RouteBase):
    schedules: List[ScheduleCreate]


class RouteResponse(RouteBase):
    id: int
    schedules: List[ScheduleResponse]


# 📌 Схемы для туров
class TourBase(BaseModel):
    name: str = Field(..., description="Название тура")
    countries: List[str] = Field(..., description="Страны, в которых проходит тур")
    duration: int = Field(..., ge=1, description="Количество дней и ночей тура")
    dates: Optional[List[str]] = Field(None, description="Гарантированные даты проведения")
    description: Optional[str] = Field(None, description="Краткое описание тура")
    meals: Optional[str] = Field(None, description="Включенные приемы пищи")
    price: float = Field(..., ge=0, description="Стоимость тура")
    extra_costs: Optional[str] = Field(None, description="Дополнительные расходы")
    accommodation: Optional[str] = Field(None, description="Описание проживания")


class TourCreate(TourBase):
    routes: List[RouteCreate]


class TourResponse(TourBase):
    id: int
    created_at: datetime
    routes: List[RouteResponse]

    class Config:
        from_attributes = True
