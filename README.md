# Dolgosrok FinBot

Долгосрочный финансовый бот (Dolgosrok FinBot) предоставляет удобный способ отслеживать финансовую отчетность компаний по их ИНН.

## Структура проекта

- **main.py:** Основной код бота.
- **last_record.py:** Парсер последней записи компании по ИНН.
- **parsers.py:** Парсер свежих отчетов компании на которые подписан пользователь.
- **database.py:** Методы для работы с базой данных.

## Установка и настройка

1. Клонируйте репозиторий:

    ```bash
    git clone https://github.com/your-username/Dolgosrok-FinBot.git
    ```

2. Перейдите в каталог проекта:

    ```bash
    cd Dolgosrok-FinBot
    ```

3. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

4. Создайте виртуальное окружение (рекомендуется):

    ```bash
    python -m venv venv
    ```

5. Активируйте виртуальное окружение:

    - Для Windows:

        ```bash
        venv\Scripts\activate
        ```

    - Для Unix или MacOS:

        ```bash
        source venv/bin/activate
        ```

6. Запустите бота:

    ```bash
    python main.py
    ```

## Использование

1. Отправьте боту команду `/start` для начала использования.

2. Выберите действие из меню:

    - **Информация:** Описание бота.
    - **Поиск:** Поиск компании по ИНН для подписки.
    - **Подписки:** Просмотр и управление активными подписками.


3. Для получения последней записи компании по ИНН, воспользуйтесь функционалом в меню "Подписки".

## База данных

Бот использует реляционную базу данных для хранения информации о подписках и отчетах. Структура базы данных описана в соответствующем файле.


