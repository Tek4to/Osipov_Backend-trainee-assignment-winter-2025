# Avito Merch Shop

## Запуск проекта
1. Убедитесь, что у вас установлены Git, Docker и Docker Compose.
2. Клонируйте репозиторий, скачав его или используя git clone https://github.com/Tek4to/Osipov_Backend-trainee-assignment-winter-2025.git
3. Перейдите в директорию проекта.
4. Запустите проект командой:
docker-compose up --build
5. Сервис будет доступен по адресу http://localhost:8080.
6. Для тестирования API, перейдите на http://localhost:8080/docs. Там вы найдёте следующие эндпоинты:
    a. Authorize (справа сверху) - позволяет авторизироваться и получить доступ к отправке монет, покупке мерча и просмотру информации о пользователе
    b. /register - Позволяет зарегестрировать нового пользователя
    c. /token - Позволяет получить JWT токен для зарегестрированного пользователя
    d. /send-coin - Отправка монет другому пользователю
    e. /buy_merch - Покупка мерча из магазина
    f. /api/info - Просмотр информации о пользователе


## Запуск тестов

Запустите команду:
docker-compose exec web pytest --cov=app --cov-report=term > app/test_results.txt
Результат тестов и процент покрытия тестами появится в текстовом файле test_results.txt в папке app

Также, в ходе разработки, обнаружил, что необходимо добавить следующие проверки в функции:
1. Проверяем, что получатель существует
2. Проверяем, что отправитель и получатель — разные пользователи
3. Не превышен лимит монет
4. Добавление обработки Query параметров для покупки нескольких товаров за раз