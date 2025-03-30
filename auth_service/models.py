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