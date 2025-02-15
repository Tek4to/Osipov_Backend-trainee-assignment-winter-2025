from sqlalchemy.orm import Session
from . import models, schemas

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_coins(db: Session, username: str, amount: int):
    db_user = get_user(db, username)
    db_user.coins += amount
    db.commit()
    db.refresh(db_user)
    return db_user

def add_inventory_item(db: Session, username: str, item: schemas.InventoryItem):
    db_user = get_user(db, username)
    db_item = models.InventoryItem(**item.dict(), owner_id=db_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_transaction(db: Session, from_user_id: int, to_user_id: int, amount: int):
    db_transaction = models.Transaction(from_user_id=from_user_id, to_user_id=to_user_id, amount=amount)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_user_transactions(db: Session, user_id: int):
    return db.query(models.Transaction).filter(
        (models.Transaction.from_user_id == user_id) | (models.Transaction.to_user_id == user_id))