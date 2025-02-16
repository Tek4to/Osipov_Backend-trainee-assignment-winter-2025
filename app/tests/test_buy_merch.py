from fastapi.testclient import TestClient
from app.main import app
from app.models import User, MerchItem
from app.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)

def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Создаем пользователя и товар
    user = User(username="testuser", password="testpassword", coins=100.0)
    item = MerchItem(name="T-shirt", price=20.0)
    db.add(user)
    db.add(item)
    db.commit()
    db.refresh(user)
    db.refresh(item)

    return db, user, item

def test_buy_merch_success():
    db, user, item = setup_db()

    # Покупаем товар
    response = client.post(
        "/buy_merch",
        json={"item_name": item.name},  # Используем название товара
        headers={"Authorization": f"Bearer {user.username}"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Merch '{item.name}' bought successfully"}

    # Проверяем, что монеты списаны
    db.refresh(user)
    assert user.coins == 80.0

    db.close()
    Base.metadata.drop_all(bind=engine)

def test_buy_merch_not_enough_coins():
    db, user, item = setup_db()

    # Устанавливаем цену товара выше, чем есть у пользователя
    item.price = 200.0
    db.commit()

    # Пытаемся купить товар
    response = client.post(
        "/buy_merch",
        json={"item_name": item.name},  # Используем название товара
        headers={"Authorization": f"Bearer {user.username}"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Not enough coins"}

    db.close()
    Base.metadata.drop_all(bind=engine)