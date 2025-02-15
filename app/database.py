from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL для подключения к PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@db:5432/avito_merch"

# Создаем движок для подключения к базе данных
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Фабрика для создания сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Функция для получения сессии (используется в зависимостях FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()