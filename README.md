# Avito Merch Shop

## Запуск проекта

1. Убедитесь, что у вас установлены Docker и Docker Compose.
2. Клонируйте репозиторий.
3. Перейдите в директорию проекта.
4. Запустите проект командой:
docker-compose up --build

5. Сервис будет доступен по адресу http://localhost:8080.
<<<<<<< V2

### 10. **Запуск проекта**

1. Открой терминал в Visual Studio Code.
2. Перейди в директорию проекта.
3. Запусти проект командой:

docker-compose up --build



## Для запуска тестов

1. Убедитесь, что у вас установлен Python 3.9 или выше. Затем создайте виртуальное окружение и установите зависимости:

python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate
pip install -r requirements.txt

docker-compose exec web pytest --cov=app --cov-report=term > app/test_results.txt
=======
6. Протестировать API вы можете на http://localhost:8080/docs
>>>>>>> main
