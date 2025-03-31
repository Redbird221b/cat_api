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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://83.220.175.252:8000",
    #"http://your-domain.com",  Add your production domain here
]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
