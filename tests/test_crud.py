import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models, crud
from app.schemas import UserCreate, InventoryItem, CoinTransfer

# Настройка тестовой базы данных
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Фикстура для создания сессии базы данных
@pytest.fixture
def db():
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        models.Base.metadata.drop_all(bind=engine)

def test_create_user(db):
    user_data = UserCreate(username="testuser", password="testpassword")
    user = crud.create_user(db, user_data)
    assert user.username == "testuser"
    assert user.password != "testpassword"  # Пароль должен быть хэширован

def test_get_user(db):
    user_data = UserCreate(username="testuser", password="testpassword")
    crud.create_user(db, user_data)
    user = crud.get_user(db, username="testuser")
    assert user.username == "testuser"

def test_update_user_coins(db):
    user_data = UserCreate(username="testuser", password="testpassword")
    user = crud.create_user(db, user_data)
    crud.update_user_coins(db, username="testuser", amount=100)
    updated_user = crud.get_user(db, username="testuser")
    assert updated_user.coins == 1100  # Начальное количество монет + 100

def test_add_inventory_item(db):
    user_data = UserCreate(username="testuser", password="testpassword")
    user = crud.create_user(db, user_data)
    item = InventoryItem(type="t-shirt", quantity=1)
    crud.add_inventory_item(db, username="testuser", item=item)
    inventory = db.query(models.InventoryItem).filter(models.InventoryItem.owner_id == user.id).first()
    assert inventory.type == "t-shirt"
    assert inventory.quantity == 1

def test_create_transaction(db):
    user1 = crud.create_user(db, UserCreate(username="user1", password="password1"))
    user2 = crud.create_user(db, UserCreate(username="user2", password="password2"))
    crud.create_transaction(db, from_user_id=user1.id, to_user_id=user2.id, amount=100)
    transaction = db.query(models.Transaction).first()
    assert transaction.from_user_id == user1.id
    assert transaction.to_user_id == user2.id
    assert transaction.amount == 100