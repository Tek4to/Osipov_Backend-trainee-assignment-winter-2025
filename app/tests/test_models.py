from app.models import MerchItem
from app.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_merch_item_creation():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Создаем товар
    item = MerchItem(name="T-shirt", price=20.0)
    db.add(item)
    db.commit()
    db.refresh(item)

    # Проверяем, что товар создан
    assert item.id is not None
    assert item.name == "T-shirt"
    assert item.price == 20.0

    db.close()
    Base.metadata.drop_all(bind=engine)