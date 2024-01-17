# database.py
import sqlite3


def create_tables():
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS subscriptions (user_id INTEGER, inn TEXT, organization_name TEXT)")
    conn.commit()
    conn.close()


def get_subscriptions(user_id):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT inn, organization_name FROM subscriptions WHERE user_id=?", (user_id,))
    subscriptions = [{"inn": row[0], "organization_name": row[1]} for row in cursor.fetchall()]
    conn.close()
    return subscriptions


# Добавим функцию для добавления подписок
def add_subscription(user_id, inn, organization_name):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    # Проверим, есть ли уже такая запись в базе данных
    cursor.execute("SELECT * FROM subscriptions WHERE user_id=? AND inn=?", (user_id, inn))
    existing_record = cursor.fetchone()

    if existing_record:
        # Если запись уже существует, обновим название организации
        cursor.execute("UPDATE subscriptions SET organization_name=? WHERE user_id=? AND inn=?", (organization_name, user_id, inn))
    else:
        # Если запись не существует, добавим новую
        cursor.execute("INSERT INTO subscriptions (user_id, inn, organization_name) VALUES (?, ?, ?)", (user_id, inn, organization_name))

    conn.commit()
    conn.close()


# Добавим функцию для удаления подписок
def remove_subscription(user_id, identifier):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    # Проверим, является ли identifier числом (ИНН), или строкой (название организации)
    if identifier.isdigit():
        cursor.execute("DELETE FROM subscriptions WHERE user_id=? AND inn=?", (user_id, identifier))
    else:
        cursor.execute("DELETE FROM subscriptions WHERE user_id=? AND organization_name=?", (user_id, identifier))

    conn.commit()
    conn.close()


def get_all_subscriptions():
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, inn, organization_name FROM subscriptions")
    all_subscriptions = {}
    for row in cursor.fetchall():
        user_id, inn, organization_name = row
        if user_id not in all_subscriptions:
            all_subscriptions[user_id] = []
        all_subscriptions[user_id].append({'inn': inn, 'organization_name': organization_name})
    conn.close()
    return all_subscriptions
