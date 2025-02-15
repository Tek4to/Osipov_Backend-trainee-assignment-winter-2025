from datetime import timedelta
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    coins = Column(Integer, default=1000)
    inventory = relationship("InventoryItem", back_populates="owner")
    transactions_sent = relationship("Transaction", foreign_keys="Transaction.from_user_id", back_populates="from_user")
    transactions_received = relationship("Transaction", foreign_keys="Transaction.to_user_id", back_populates="to_user")

class InventoryItem(Base):  # Исправлено: Base вместо BaseModel
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    quantity = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="inventory")

class Transaction(Base):  # Исправлено: Base вместо BaseModel
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id"))
    to_user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="transactions_sent")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="transactions_received")

class MerchItem(Base):  # Исправлено: Base вместо BaseModel
    __tablename__ = "merch_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    price = Column(Integer)