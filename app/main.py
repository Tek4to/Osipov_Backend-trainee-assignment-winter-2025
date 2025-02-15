from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from fastapi import FastAPI
from . import models, database
from .api import router
import time

app = FastAPI()

# Подключаем роутер
app.include_router(router)

# Функция для проверки доступности базы данных
def wait_for_db():
    retries = 5
    while retries > 0:
        try:
            engine = create_engine(database.SQLALCHEMY_DATABASE_URL)
            engine.connect()
            break
        except OperationalError:
            retries -= 1
            time.sleep(5)
            if retries == 0:
                raise

@app.on_event("startup")
def startup():
    # Ждём, пока база данных станет доступной
    wait_for_db()

    # Создаём таблицы, если их нет
    models.Base.metadata.create_all(bind=database.engine)

    # Добавляем товары, если их нет в БД
    db = database.SessionLocal()
    try:
        items = [
            {"name": "t-shirt", "price": 80},
            {"name": "cup", "price": 20},
            {"name": "book", "price": 50},
            {"name": "pen", "price": 10},
            {"name": "powerbank", "price": 200},
            {"name": "hoody", "price": 300},
            {"name": "umbrella", "price": 200},
            {"name": "socks", "price": 10},
            {"name": "wallet", "price": 50},
            {"name": "pink-hoody", "price": 500},
        ]
        for item in items:
            if not db.query(models.MerchItem).filter(models.MerchItem.name == item["name"]).first():
                db_item = models.MerchItem(name=item["name"], price=item["price"])
                db.add(db_item)
        db.commit()
    finally:
        db.close()