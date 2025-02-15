import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import models, database
from app.schemas import UserCreate, MerchItem, CoinTransfer

# Настройка тестового клиента
client = TestClient(app)

# Фикстура для тестовой базы данных
@pytest.fixture
def db():
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        models.Base.metadata.drop_all(bind=engine)

def test_buy_merch(db):
    # Регистрируем пользователя
    user_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/register", json=user_data)
    assert response.status_code == 200

    # Получаем токен
    response = client.post("/token", data={"username": "testuser", "password": "testpassword"})
    token = response.json()["access_token"]

    # Покупаем товар
    item_data = {"name": "t-shirt", "price": 80}
    response = client.post("/buy_merch", json=item_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Merch bought successfully"}

    # Проверяем, что монеты списались
    response = client.get("/api/info", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["coins"] == 920  # 1000 - 80

    # Проверяем, что товар добавился в инвентарь
    assert len(response.json()["inventory"]) == 1
    assert response.json()["inventory"][0]["type"] == "t-shirt"
    assert response.json()["inventory"][0]["quantity"] == 1

def test_send_coin(db):
    # Регистрируем двух пользователей
    user1_data = {"username": "user1", "password": "password1"}
    user2_data = {"username": "user2", "password": "password2"}
    client.post("/register", json=user1_data)
    client.post("/register", json=user2_data)

    # Получаем токен для user1
    response = client.post("/token", data={"username": "user1", "password": "password1"})
    token = response.json()["access_token"]

    # Отправляем монеты от user1 к user2
    transfer_data = {"to_user": "user2", "amount": 100}
    response = client.post("/send_coin", json=transfer_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Coins transferred successfully"}

    # Проверяем, что монеты списались у user1
    response = client.get("/api/info", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["coins"] == 900  # 1000 - 100

    # Проверяем, что монеты добавились у user2
    response = client.post("/token", data={"username": "user2", "password": "password2"})
    token_user2 = response.json()["access_token"]
    response = client.get("/api/info", headers={"Authorization": f"Bearer {token_user2}"})
    assert response.status_code == 200
    assert response.json()["coins"] == 1100  # 1000 + 100