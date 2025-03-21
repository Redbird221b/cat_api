from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import json
import routes

# Создаём таблицы в БД (если их нет)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Указываем конкретный источник (или несколько)
    allow_credentials=True,  # Позволяет передавать куки (refresh_token)
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Разрешаем только нужные методы
    allow_headers=["Authorization", "Content-Type"],  # Разрешаем заголовки
)

@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    print("❌ Ошибка валидации запроса:", json.dumps(exc.errors(), indent=2, ensure_ascii=False))  # Вывод в консоль
    return JSONResponse(
        status_code=422,
        content={"detail": jsonable_encoder(exc.errors(), exclude={"input"})}
    )

# Подключаем маршруты
app.include_router(routes.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8222)
