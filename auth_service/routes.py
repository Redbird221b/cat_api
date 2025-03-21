from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Tour, Route, Schedule
from utils import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from schemas import TourCreate, TourResponse, RouteCreate, RouteResponse, ScheduleCreate, ScheduleResponse
from typing import List

router = APIRouter()


# Получение сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Функция для генерации и отправки токенов
def generate_tokens(response: Response, user: User, db: Session):
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    user.refresh_token = refresh_token
    db.commit()

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="None"
    )

    return {"access_token": access_token, "token_type": "bearer"}


# Регистрация
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(email=email, hashed_password=hash_password(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}


# Авторизация
@router.post("/login")
async def login(request: Request, response: Response, db: Session = Depends(get_db)):
    body = await request.json()
    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    db_user = db.query(User).filter(User.email == email).first()
    if not db_user or not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return generate_tokens(response, db_user, db)


# Обновление access токена
@router.post("/refresh")
async def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token provided")

    payload = decode_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()

    if not user or user.refresh_token != refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return generate_tokens(response, user, db)


# Выход (logout)
@router.post("/logout")
async def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        user = db.query(User).filter(User.refresh_token == refresh_token).first()
        if user:
            user.refresh_token = None
            db.commit()

    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}


# ========================== ТУРЫ ==========================

# ✅ Создание тура с маршрутами и расписанием
@router.post("/tours/", response_model=TourResponse)
def create_tour(tour_data: TourCreate, db: Session = Depends(get_db)):
    new_tour = Tour(
        name=tour_data.name,
        countries=tour_data.countries,
        duration=tour_data.duration,
        dates=tour_data.dates,
        description=tour_data.description,
        meals=tour_data.meals,
        price=tour_data.price,
        extra_costs=tour_data.extra_costs,
        accommodation=tour_data.accommodation
    )
    db.add(new_tour)
    db.commit()
    db.refresh(new_tour)

    # Создание маршрутов и расписания
    for route_data in tour_data.routes:
        new_route = Route(
            tour_id=new_tour.id,
            cities=route_data.cities,
            description=route_data.description
        )
        db.add(new_route)
        db.commit()
        db.refresh(new_route)

        for schedule_data in route_data.schedules:
            new_schedule = Schedule(
                route_id=new_route.id,
                day_number=schedule_data.day_number,
                activities=schedule_data.activities,
                image=schedule_data.image
            )
            db.add(new_schedule)
    db.commit()

    return new_tour


# ✅ Получение всех туров
@router.get("/tours/", response_model=List[TourResponse])
def get_all_tours(db: Session = Depends(get_db)):
    return db.query(Tour).all()


# ✅ Получение тура по ID
@router.get("/tours/{tour_id}", response_model=TourResponse)
def get_tour(tour_id: int, db: Session = Depends(get_db)):
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    return tour


# ✅ Удаление тура
@router.delete("/tours/{tour_id}")
def delete_tour(tour_id: int, db: Session = Depends(get_db)):
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    db.delete(tour)
    db.commit()
    return {"message": "Tour deleted successfully"}


# ✅ Обновление тура
@router.put("/tours/{tour_id}", response_model=TourResponse)
def update_tour(tour_id: int, tour_data: TourCreate, db: Session = Depends(get_db)):
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    # Обновляем основные данные тура
    tour.name = tour_data.name
    tour.countries = tour_data.countries
    tour.duration = tour_data.duration
    tour.dates = tour_data.dates
    tour.description = tour_data.description
    tour.meals = tour_data.meals
    tour.price = tour_data.price
    tour.extra_costs = tour_data.extra_costs
    tour.accommodation = tour_data.accommodation
    db.commit()

    # Удаляем старые маршруты и расписание
    db.query(Route).filter(Route.tour_id == tour_id).delete()
    db.commit()

    # Создаём новые маршруты и расписание
    for route_data in tour_data.routes:
        new_route = Route(
            tour_id=tour.id,
            cities=route_data.cities,
            description=route_data.description
        )
        db.add(new_route)
        db.commit()
        db.refresh(new_route)

        for schedule_data in route_data.schedules:
            new_schedule = Schedule(
                route_id=new_route.id,
                day_number=schedule_data.day_number,
                activities=schedule_data.activities,
                image=schedule_data.image
            )
            db.add(new_schedule)
    db.commit()

    return tour


# ========================== МАРШРУТЫ ==========================

# ✅ Создание маршрута для существующего тура
@router.post("/routes/{tour_id}", response_model=RouteResponse)
def create_route(tour_id: int, route_data: RouteCreate, db: Session = Depends(get_db)):
    if not db.query(Tour).filter(Tour.id == tour_id).first():
        raise HTTPException(status_code=404, detail="Tour not found")

    new_route = Route(
        tour_id=tour_id,
        cities=route_data.cities,
        description=route_data.description
    )
    db.add(new_route)
    db.commit()
    db.refresh(new_route)

    for schedule_data in route_data.schedules:
        new_schedule = Schedule(
            route_id=new_route.id,
            day_number=schedule_data.day_number,
            activities=schedule_data.activities,
            image=schedule_data.image
        )
        db.add(new_schedule)
    db.commit()

    return new_route


@router.put("/routes/{route_id}", response_model=RouteResponse)
def update_route(route_id: int, route_data: RouteCreate, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    # Обновляем данные маршрута
    route.cities = route_data.cities
    route.description = route_data.description
    db.commit()

    # Удаляем старое расписание
    db.query(Schedule).filter(Schedule.route_id == route_id).delete()

    # Добавляем новое расписание
    for schedule_data in route_data.schedules:
        new_schedule = Schedule(
            route_id=route_id,
            day_number=schedule_data.day_number,
            activities=schedule_data.activities,
            image=schedule_data.image
        )
        db.add(new_schedule)
    db.commit()

    return route


# ✅ Удаление маршрута
@router.delete("/routes/{route_id}")
def delete_route(route_id: int, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    # Удаляем маршрут вместе с расписанием
    db.delete(route)
    db.commit()
    return {"message": "Route deleted successfully"}


# ✅ Получение всех маршрутов для конкретного тура
@router.get("/routes/{tour_id}", response_model=List[RouteResponse])
def get_routes(tour_id: int, db: Session = Depends(get_db)):
    return db.query(Route).filter(Route.tour_id == tour_id).all()


# ========================== РАСПИСАНИЕ ==========================

# ✅ Добавление расписания для маршрута
@router.post("/schedules/{route_id}", response_model=ScheduleResponse)
def create_schedule(route_id: int, schedule_data: ScheduleCreate, db: Session = Depends(get_db)):
    if not db.query(Route).filter(Route.id == route_id).first():
        raise HTTPException(status_code=404, detail="Route not found")

    new_schedule = Schedule(
        route_id=route_id,
        day_number=schedule_data.day_number,
        activities=schedule_data.activities,
        image=schedule_data.image
    )
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule


# ✅ Получение расписания для маршрута
@router.get("/schedules/{route_id}", response_model=List[ScheduleResponse])
def get_schedule(route_id: int, db: Session = Depends(get_db)):
    return db.query(Schedule).filter(Schedule.route_id == route_id).all()


# ✅ Обновление дня расписания
@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(schedule_id: int, schedule_data: ScheduleCreate, db: Session = Depends(get_db)):
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # Обновляем данные расписания
    schedule.day_number = schedule_data.day_number
    schedule.activities = schedule_data.activities
    schedule.image = schedule_data.image
    db.commit()
    db.refresh(schedule)

    return schedule


# ✅ Удаление дня расписания
@router.delete("/schedules/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    db.delete(schedule)
    db.commit()
    return {"message": "Schedule deleted successfully"}
