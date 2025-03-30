from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# 📌 Схемы для дней маршрута
class ScheduleBase(BaseModel):
    day_number: int = Field(..., ge=1, description="Номер дня маршрута (начинается с 1)")
    activities_ru: Optional[str] = Field(None, description="Описание событий на русском")
    activities_en: Optional[str] = Field(None, description="Описание событий на английском")
    image: Optional[str] = Field(None, description="Ссылка на изображение")


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleResponse(ScheduleBase):
    id: int


# 📌 Схемы для маршрутов
class RouteBase(BaseModel):
    cities: List[str] = Field(..., description="Список основных городов или достопримечательностей")
    description_ru: Optional[str] = Field(None, description="Описание маршрута на русском")
    description_en: Optional[str] = Field(None, description="Описание маршрута на английском")


class RouteCreate(RouteBase):
    schedules: List[ScheduleCreate]


class RouteResponse(RouteBase):
    id: int
    schedules: List[ScheduleResponse]


# 📌 Схемы для туров
class TourBase(BaseModel):
    name_ru: str = Field(..., description="Название тура на русском")
    name_en: str = Field(..., description="Название тура на английском")
    countries: List[str] = Field(..., description="Страны, в которых проходит тур")
    duration: int = Field(..., ge=1, description="Количество дней и ночей тура")
    dates: Optional[List[str]] = Field(None, description="Гарантированные даты проведения")
    description_ru: Optional[str] = Field(None, description="Краткое описание тура на русском")
    description_en: Optional[str] = Field(None, description="Краткое описание тура на английском")
    meals_ru: Optional[str] = Field(None, description="Включенные приемы пищи на русском")
    meals_en: Optional[str] = Field(None, description="Включенные приемы пищи на английском")
    price: float = Field(..., ge=0, description="Стоимость тура")
    extra_costs_ru: Optional[str] = Field(None, description="Дополнительные расходы на русском")
    extra_costs_en: Optional[str] = Field(None, description="Дополнительные расходы на английском")
    accommodation_ru: Optional[str] = Field(None, description="Описание проживания на русском")
    accommodation_en: Optional[str] = Field(None, description="Описание проживания на английском")
    category: str
    tags: List[str]


class TourCreate(TourBase):
    routes: List[RouteCreate]


class TourResponse(TourBase):
    id: int
    created_at: datetime
    routes: List[RouteResponse]

    class Config:
        from_attributes = True
