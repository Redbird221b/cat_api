from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, DateTime, ARRAY, func
from database import Base
import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    refresh_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())


class Tour(Base):
    __tablename__ = "tours"

    id = Column(Integer, primary_key=True, index=True)
    name_ru = Column(Text, nullable=False)
    name_en = Column(Text, nullable=False)
    countries = Column(ARRAY(String), nullable=False)
    duration = Column(Integer, nullable=False)
    dates = Column(ARRAY(String), nullable=True)
    description_ru = Column(Text, nullable=True)
    description_en = Column(Text, nullable=True)
    meals_ru = Column(Text, nullable=True)
    meals_en = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    extra_costs_ru = Column(Text, nullable=True)
    extra_costs_en = Column(Text, nullable=True)
    accommodation_ru = Column(Text, nullable=True)
    accommodation_en = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    category = Column(String, nullable=False)
    tags = Column(ARRAY(String), nullable=False)

    routes = relationship("Route", back_populates="tour", cascade="all, delete-orphan")


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=False)
    cities = Column(ARRAY(String), nullable=False)
    description_ru = Column(Text, nullable=True)
    description_en = Column(Text, nullable=True)

    tour = relationship("Tour", back_populates="routes")
    schedules = relationship("Schedule", back_populates="route", cascade="all, delete-orphan")


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    day_number = Column(Integer, nullable=False)
    activities_ru = Column(Text, nullable=True)
    activities_en = Column(Text, nullable=True)
    image = Column(Text, nullable=True)

    route = relationship("Route", back_populates="schedules")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Для авторизованных пользователей

    # Паспортные данные
    last_name = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    gender = Column(String, nullable=False)  # Например, "male", "female"
    citizenship = Column(String, nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    passport_number = Column(String, nullable=False)  # № паспорта
    passport_issue_date = Column(DateTime, nullable=False)  # Дата выдачи паспорта
    passport_expiry_date = Column(DateTime, nullable=False)  # Срок действия паспорта

    # Контактные данные
    home_address = Column(Text, nullable=False)  # Домашний адрес (прописка)
    phone_numbers = Column(ARRAY(String), nullable=False)  # Ваш номер телефона (список)
    email = Column(String, nullable=False)
    emergency_contact_phones = Column(ARRAY(String), nullable=False)  # Телефоны близких родственников
    emergency_contact_emails = Column(ARRAY(String), nullable=False)  # E-mailы близких родственников
    workplace = Column(String, nullable=True)  # Место работы/должность

    # Пакет
    package_type = Column(String, nullable=False)  # Укажите желаемый пакет
    altitude_experience = Column(Text, nullable=True)  # Ваш высотный опыт
    additional_info = Column(Text, nullable=True)  # Доп. информация

    # Перечень запрашиваемых услуг
    additional_services = Column(ARRAY(String), nullable=True)  # Чекбоксы с услугами

    # Прибытие
    arrival_airport = Column(String, nullable=False)
    arrival_date = Column(DateTime, nullable=False)
    arrival_time = Column(String, nullable=False)  # Например, "14:30"
    arrival_flight_number = Column(String, nullable=False)
    arrival_osh_to_base_date = Column(DateTime, nullable=True)  # Переезд Ош-Базовый лагерь (дата)

    # Выбытие
    departure_airport = Column(String, nullable=False)
    departure_date = Column(DateTime, nullable=False)
    departure_time = Column(String, nullable=False)
    departure_flight_number = Column(String, nullable=False)
    departure_osh_to_base_date = Column(DateTime, nullable=True)  # Переезд Ош-Базовый лагерь (дата)

    # Информация о страховке
    insurance_policy_number = Column(String, nullable=True)  # № страхового полиса
    insurance_coverage = Column(Float, nullable=True)  # Сумма покрытия
    insurance_company_name = Column(String, nullable=True)
    insurance_company_phone = Column(String, nullable=True)
    emergency_contact_phone = Column(String, nullable=True)  # Телефон контактного лица

    created_at = Column(DateTime, default=func.now())

    # Связи
    tour = relationship("Tour")
    user = relationship("User")
