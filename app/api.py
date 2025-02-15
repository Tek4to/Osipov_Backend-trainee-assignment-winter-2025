from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import crud, schemas, database, auth

router = APIRouter()

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    db_user = crud.create_user(db=db, user=schemas.UserCreate(username=user.username, password=hashed_password))
    return db_user

@router.post("/send_coin")
def send_coin(transfer: schemas.CoinTransfer, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    sender = crud.get_user(db, username=transfer.to_user)
    if not sender:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.coins < transfer.amount:
        raise HTTPException(status_code=400, detail="Not enough coins")
    crud.update_user_coins(db, username=current_user.username, amount=-transfer.amount)
    crud.update_user_coins(db, username=transfer.to_user, amount=transfer.amount)
    crud.create_transaction(db, from_user_id=current_user.id, to_user_id=sender.id, amount=transfer.amount)
    return {"message": "Coins transferred successfully"}

@router.post("/buy_merch")
def buy_merch(item: schemas.MerchItem, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    if current_user.coins < item.price:
        raise HTTPException(status_code=400, detail="Not enough coins")
    crud.update_user_coins(db, username=current_user.username, amount=-item.price)
    crud.add_inventory_item(db, username=current_user.username, item=schemas.InventoryItem(type=item.name, quantity=1))
    return {"message": "Merch bought successfully"}

@router.get("/api/info", response_model=schemas.InfoResponse)
def get_info(current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    user = crud.get_user(db, username=current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    transactions = crud.get_user_transactions(db, user.id)
    received = [{"fromUser": t.from_user.username, "amount": t.amount} for t in transactions if t.to_user_id == user.id]
    sent = [{"toUser": t.to_user.username, "amount": t.amount} for t in transactions if t.from_user_id == user.id]

    return {
        "coins": user.coins,
        "inventory": user.inventory,
        "coinHistory": {
            "received": received,
            "sent": sent
        }
    }