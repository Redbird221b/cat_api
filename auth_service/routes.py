from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from utils import hash_password, verify_password, create_access_token, create_refresh_token, decode_token

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
