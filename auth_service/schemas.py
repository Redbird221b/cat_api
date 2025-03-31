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


# Новые схемы для заявок
class ApplicationBase(BaseModel):
    tour_id: int = Field(..., description="ID тура")
    user_id: Optional[int] = Field(None, description="ID пользователя (если авторизован)")

    # Паспортные данные
    last_name: str = Field(..., description="Фамилия")
    first_name: str = Field(..., description="Имя")
    middle_name: Optional[str] = Field(None, description="Отчество")
    gender: str = Field(..., description="Пол (male/female)")
    citizenship: str = Field(..., description="Гражданство")
    date_of_birth: datetime = Field(..., description="Дата рождения")
    passport_number: str = Field(..., description="Номер паспорта")
    passport_issue_date: datetime = Field(..., description="Дата выдачи паспорта")
    passport_expiry_date: datetime = Field(..., description="Срок действия паспорта")

    # Контактные данные
    home_address: str = Field(..., description="Домашний адрес (прописка)")
    phone_numbers: List[str] = Field(..., description="Ваши номера телефонов")
    email: str = Field(..., description="E-mail")
    emergency_contact_phones: List[str] = Field(..., description="Телефоны близких родственников")
    emergency_contact_emails: List[str] = Field(..., description="E-mailы близких родственников")
    workplace: Optional[str] = Field(None, description="Место работы/должность")

    # Пакет
    package_type: str = Field(..., description="Тип пакета")
    altitude_experience: Optional[str] = Field(None, description="Ваш высотный опыт")
    additional_info: Optional[str] = Field(None, description="Дополнительная информация")

    # Перечень запрашиваемых услуг
    additional_services: Optional[List[str]] = Field(None, description="Дополнительные услуги")

    # Прибытие
    arrival_airport: str = Field(..., description="Аэропорт прибытия")
    arrival_date: datetime = Field(..., description="Дата прибытия")
    arrival_time: str = Field(..., description="Время прибытия")
    arrival_flight_number: str = Field(..., description="Номер рейса прибытия")
    arrival_osh_to_base_date: Optional[datetime] = Field(None, description="Дата переезда Ош-Базовый лагерь")

    # Выбытие
    departure_airport: str = Field(..., description="Аэропорт выбытия")
    departure_date: datetime = Field(..., description="Дата выбытия")
    departure_time: str = Field(..., description="Время выбытия")
    departure_flight_number: str = Field(..., description="Номер рейса выбытия")
    departure_osh_to_base_date: Optional[datetime] = Field(None, description="Дата переезда Ош-Базовый лагерь")

    # Информация о страховке
    insurance_policy_number: Optional[str] = Field(None, description="Номер страхового полиса")
    insurance_coverage: Optional[float] = Field(None, description="Сумма покрытия")
    insurance_company_name: Optional[str] = Field(None, description="Название страховой компании")
    insurance_company_phone: Optional[str] = Field(None, description="Телефон страховой компании")
    emergency_contact_phone: Optional[str] = Field(None,
                                                   description="Телефон контактного лица на непредвиденные случаи")


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationResponse(ApplicationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
