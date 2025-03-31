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
    allow_origins=["http://localhost:5173", "77.221.158.99:80"],  # Указываем конкретный источник (или несколько)
    allow_credentials=True,  # Позволяет передавать куки (refresh_token)
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Разрешаем только нужные методы
    allow_headers=["Authorization", "Content-Type"],  # Разрешаем заголовки
)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    error_details = []
    for err in exc.errors():
        field_path = " → ".join(map(str, err["loc"]))  # Преобразуем список loc в читаемую строку
        error_message = f"Ошибка в поле '{field_path}': {err['msg']}"
        error_details.append(error_message)

    # Выводим в консоль в более удобочитаемом формате
    print("❌ Ошибка валидации запроса:")
    for error in error_details:
        print(f"  - {error}")

    return JSONResponse(
        status_code=422,
        content={"detail": error_details}
    )


# Подключаем маршруты
app.include_router(routes.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8222)
