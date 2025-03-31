from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Tour, Route, Schedule, Application
from utils import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from schemas import TourCreate, TourResponse, RouteCreate, RouteResponse, ScheduleCreate, ScheduleResponse, \
    ApplicationCreate, ApplicationResponse, UserResponse
from typing import List

router = APIRouter()


# Получение сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Зависимость для проверки токена
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


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


# Регистрация (для администраторов)
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: Request, db: Session = Depends(get_db)):
    body = await request.json()  # Добавляем await
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


# Авторизация (для администраторов)
@router.post("/login")
async def login(request: Request, response: Response, db: Session = Depends(get_db)):
    body = await request.json()  # Добавляем await
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


# Получение списка пользователей
@router.get("/users/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), ):
    users = db.query(User).all()
    return users


# ========================== ТУРЫ ==========================

@router.post("/tours/", response_model=TourResponse)
def create_tour(tour_data: TourCreate, db: Session = Depends(get_db)):
    new_tour = Tour(
        name_ru=tour_data.name_ru,
        name_en=tour_data.name_en,
        countries=tour_data.countries,
        duration=tour_data.duration,
        dates=tour_data.dates,
        description_ru=tour_data.description_ru,
        description_en=tour_data.description_en,
        meals_ru=tour_data.meals_ru,
        meals_en=tour_data.meals_en,
        price=tour_data.price,
        extra_costs_ru=tour_data.extra_costs_ru,
        extra_costs_en=tour_data.extra_costs_en,
        accommodation_ru=tour_data.accommodation_ru,
        accommodation_en=tour_data.accommodation_en,
        category=tour_data.category,
        tags=tour_data.tags
    )
    db.add(new_tour)
    db.commit()
    db.refresh(new_tour)

    for route_data in tour_data.routes:
        new_route = Route(
            tour_id=new_tour.id,
            cities=route_data.cities,
            description_ru=route_data.description_ru,
            description_en=route_data.description_en
        )
        db.add(new_route)
        db.commit()
        db.refresh(new_route)

        for schedule_data in route_data.schedules:
            new_schedule = Schedule(
                route_id=new_route.id,
                day_number=schedule_data.day_number,
                activities_ru=schedule_data.activities_ru,
                activities_en=schedule_data.activities_en,
                image=schedule_data.image
            )
            db.add(new_schedule)
    db.commit()

    return new_tour


@router.get("/tours/", response_model=List[TourResponse])
def get_all_tours(db: Session = Depends(get_db)):
    return db.query(Tour).all()


@router.get("/tours/{tour_id}", response_model=TourResponse)
def get_tour(tour_id: int, db: Session = Depends(get_db)):
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    return tour


@router.delete("/tours/{tour_id}")
def delete_tour(tour_id: int, db: Session = Depends(get_db)):
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    db.delete(tour)
    db.commit()
    return {"message": "Tour deleted successfully"}


@router.put("/tours/{tour_id}", response_model=TourResponse)
def update_tour(tour_id: int, tour_data: TourCreate, db: Session = Depends(get_db),
                ):
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    tour.name_ru = tour_data.name_ru
    tour.name_en = tour_data.name_en
    tour.countries = tour_data.countries
    tour.duration = tour_data.duration
    tour.dates = tour_data.dates
    tour.description_ru = tour_data.description_ru
    tour.description_en = tour_data.description_en
    tour.meals_ru = tour_data.meals_ru
    tour.meals_en = tour_data.meals_en
    tour.price = tour_data.price
    tour.extra_costs_ru = tour_data.extra_costs_ru
    tour.extra_costs_en = tour_data.extra_costs_en
    tour.accommodation_ru = tour_data.accommodation_ru
    tour.accommodation_en = tour_data.accommodation_en
    tour.category = tour_data.category
    tour.tags = tour_data.tags
    db.commit()

    db.query(Route).filter(Route.tour_id == tour_id).delete()
    db.commit()

    for route_data in tour_data.routes:
        new_route = Route(
            tour_id=tour.id,
            cities=route_data.cities,
            description_ru=route_data.description_ru,
            description_en=route_data.description_en
        )
        db.add(new_route)
        db.commit()
        db.refresh(new_route)

        for schedule_data in route_data.schedules:
            new_schedule = Schedule(
                route_id=new_route.id,
                day_number=schedule_data.day_number,
                activities_ru=schedule_data.activities_ru,
                activities_en=schedule_data.activities_en,
                image=schedule_data.image
            )
            db.add(new_schedule)
    db.commit()

    return tour


# ========================== МАРШРУТЫ ==========================

@router.post("/routes/{tour_id}", response_model=RouteResponse)
def create_route(tour_id: int, route_data: RouteCreate, db: Session = Depends(get_db)):
    if not db.query(Tour).filter(Tour.id == tour_id).first():
        raise HTTPException(status_code=404, detail="Tour not found")

    new_route = Route(
        tour_id=tour_id,
        cities=route_data.cities,
        description_ru=route_data.description_ru,
        description_en=route_data.description_en
    )
    db.add(new_route)
    db.commit()
    db.refresh(new_route)

    for schedule_data in route_data.schedules:
        new_schedule = Schedule(
            route_id=new_route.id,
            day_number=schedule_data.day_number,
            activities_ru=schedule_data.activities_ru,
            activities_en=schedule_data.activities_en,
            image=schedule_data.image
        )
        db.add(new_schedule)
    db.commit()

    return new_route


@router.put("/routes/{route_id}", response_model=RouteResponse)
def update_route(route_id: int, route_data: RouteCreate, db: Session = Depends(get_db),
                 ):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    route.cities = route_data.cities
    route.description_ru = route_data.description_ru
    route.description_en = route_data.description_en
    db.commit()

    db.query(Schedule).filter(Schedule.route_id == route_id).delete()

    for schedule_data in route_data.schedules:
        new_schedule = Schedule(
            route_id=route_id,
            day_number=schedule_data.day_number,
            activities_ru=schedule_data.activities_ru,
            activities_en=schedule_data.activities_en,
            image=schedule_data.image
        )
        db.add(new_schedule)
    db.commit()

    return route


@router.delete("/routes/{route_id}")
def delete_route(route_id: int, db: Session = Depends(get_db), ):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    db.delete(route)
    db.commit()
    return {"message": "Route deleted successfully"}


@router.get("/routes/{tour_id}", response_model=List[RouteResponse])
def get_routes(tour_id: int, db: Session = Depends(get_db)):
    return db.query(Route).filter(Route.tour_id == tour_id).all()


# ========================== РАСПИСАНИЕ ==========================

@router.post("/schedules/{route_id}", response_model=ScheduleResponse)
def create_schedule(route_id: int, schedule_data: ScheduleCreate, db: Session = Depends(get_db),
                    ):
    if not db.query(Route).filter(Route.id == route_id).first():
        raise HTTPException(status_code=404, detail="Route not found")

    new_schedule = Schedule(
        route_id=route_id,
        day_number=schedule_data.day_number,
        activities_ru=schedule_data.activities_ru,
        activities_en=schedule_data.activities_en,
        image=schedule_data.image
    )
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule


@router.get("/schedules/{route_id}", response_model=List[ScheduleResponse])
def get_schedule(route_id: int, db: Session = Depends(get_db)):
    return db.query(Schedule).filter(Schedule.route_id == route_id).all()


@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(schedule_id: int, schedule_data: ScheduleCreate, db: Session = Depends(get_db),
                    ):
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    schedule.day_number = schedule_data.day_number
    schedule.activities_ru = schedule_data.activities_ru
    schedule.activities_en = schedule_data.activities_en
    schedule.image = schedule_data.image
    db.commit()
    db.refresh(schedule)

    return schedule


@router.delete("/schedules/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db), ):
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    db.delete(schedule)
    db.commit()
    return {"message": "Schedule deleted successfully"}


# ========================== ЗАЯВКИ ==========================

@router.post("/applications/", response_model=ApplicationResponse)
def create_application(application_data: ApplicationCreate, db: Session = Depends(get_db)):
    new_application = Application(
        last_name=application_data.last_name,
        first_name=application_data.first_name,
        middle_name=application_data.middle_name,
        gender=application_data.gender,
        citizenship=application_data.citizenship,
        date_of_birth=application_data.date_of_birth,
        passport_number=application_data.passport_number,
        passport_issue_date=application_data.passport_issue_date,
        passport_expiry_date=application_data.passport_expiry_date,
        home_address=application_data.home_address,
        phone_numbers=application_data.phone_numbers,
        email=application_data.email,
        emergency_contact_phones=application_data.emergency_contact_phones,
        emergency_contact_emails=application_data.emergency_contact_emails,
        workplace=application_data.workplace,
        package_type=application_data.package_type,
        altitude_experience=application_data.altitude_experience,
        additional_info=application_data.additional_info,
        additional_services=application_data.additional_services,
        arrival_airport=application_data.arrival_airport,
        arrival_date=application_data.arrival_date,
        arrival_time=application_data.arrival_time,
        arrival_flight_number=application_data.arrival_flight_number,
        arrival_osh_to_base_date=application_data.arrival_osh_to_base_date,
        departure_airport=application_data.departure_airport,
        departure_date=application_data.departure_date,
        departure_time=application_data.departure_time,
        departure_flight_number=application_data.departure_flight_number,
        departure_osh_to_base_date=application_data.departure_osh_to_base_date,
        insurance_policy_number=application_data.insurance_policy_number,
        insurance_coverage=application_data.insurance_coverage,
        insurance_company_name=application_data.insurance_company_name,
        insurance_company_phone=application_data.insurance_company_phone,
        emergency_contact_phone=application_data.emergency_contact_phone
    )

    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    return new_application


@router.get("/applications/", response_model=List[ApplicationResponse])
def get_applications(db: Session = Depends(get_db)):
    return db.query(Application).all()


@router.get("/applications/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: int, db: Session = Depends(get_db), ):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application
