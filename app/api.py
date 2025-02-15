from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import crud, schemas, database, auth
from . import models

router = APIRouter()

# Максимальное количество монет
MAX_COINS = 1000000

# Эндпоинт для получения токена (авторизация)
@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    # Аутентификация пользователя
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    
    # Если пользователь не найден или пароль неверный
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создание токена доступа
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Возвращаем токен
    return {"access_token": access_token, "token_type": "bearer"}

# Эндпоинт для регистрации пользователя
@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Проверяем, что пользователь с таким именем не существует
    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Хешируем пароль и создаем нового пользователя
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, password=hashed_password, coins=0)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Эндпоинт для перевода монет
@router.post("/send_coin")
def send_coin(transfer: schemas.TransferCoin, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Получаем отправителя и получателя из базы данных
    sender = db.query(models.User).filter(models.User.username == current_user.username).first()
    receiver = db.query(models.User).filter(models.User.username == transfer.receiver_username).first()

    # Проверяем, что получатель существует
    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receiver not found",
        )

    # Проверяем, что отправитель и получатель — разные пользователи
    if sender.username == receiver.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send coins to yourself",
        )

    # Проверяем, что у отправителя достаточно монет
    if sender.coins < transfer.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough coins",
        )

    # Проверяем, что у получателя не превышен лимит монет
    if receiver.coins + transfer.amount > MAX_COINS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Receiver coin limit exceeded",
        )

    # Выполняем перевод
    sender.coins -= transfer.amount
    receiver.coins += transfer.amount

    # Сохраняем изменения в базе данных
    db.commit()
    db.refresh(sender)
    db.refresh(receiver)

    return {"message": "Transfer successful"}

# Эндпоинт для покупки товара
@router.post("/buy_merch")
def buy_merch(item: schemas.MerchItem, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Получаем товар из базы данных
    db_item = db.query(models.MerchItem).filter(models.MerchItem.name == item.name).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Проверяем, что у пользователя достаточно монет
    if current_user.coins < db_item.price:
        raise HTTPException(status_code=400, detail="Not enough coins")

    # Проверяем, есть ли товар в инвентаре
    inventory_item = db.query(models.InventoryItem).filter(
        models.InventoryItem.owner_id == current_user.id,
        models.InventoryItem.type == db_item.name
    ).first()

    if inventory_item:
        # Если товар уже есть, увеличиваем количество
        inventory_item.quantity += 1
    else:
        # Если товара нет, добавляем его в инвентарь
        inventory_item = models.InventoryItem(type=db_item.name, quantity=1, owner_id=current_user.id)
        db.add(inventory_item)

    # Списание монет
    current_user.coins -= db_item.price
    db.commit()

    return {"message": "Merch bought successfully"}

# Эндпоинт для получения информации о пользователе
@router.get("/api/info", response_model=schemas.InfoResponse)
def get_info(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    # Получаем транзакции пользователя
    transactions = crud.get_user_transactions(db, current_user.id)
    received = [{"fromUser": t.from_user.username, "amount": t.amount} for t in transactions if t.to_user_id == current_user.id]
    sent = [{"toUser": t.to_user.username, "amount": t.amount} for t in transactions if t.from_user_id == current_user.id]

    return {
        "coins": current_user.coins,
        "inventory": current_user.inventory,
        "coinHistory": {
            "received": received,
            "sent": sent
        }
    }