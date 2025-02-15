from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str
    coins: int

    class Config:
        from_attributes = True

class InventoryItem(BaseModel):
    type: str
    quantity: int

    class Config:
        from_attributes = True

class CoinTransfer(BaseModel):
    to_user: str
    amount: int

class MerchItem(BaseModel):
    name: str
    price: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class InfoResponse(BaseModel):
    coins: int
    inventory: List[InventoryItem]
    coinHistory: dict