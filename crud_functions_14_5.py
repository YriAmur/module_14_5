import sqlite3

DB_NAME = 'Products.db'

def initiate_db():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    # Создание таблицы Products
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL
    )
    ''')

    # Проверка на наличие продуктов и добавление, если пусто
    cursor.execute('SELECT COUNT(*) FROM Products')
    if cursor.fetchone()[0] == 0:
        # Добавляем продукты, если таблица пустая
        products = [
            ('vitamin A', 'Описание 1', 100),
            ('vitamin B', 'Описание 2', 200),
            ('vitamin C', 'Описание 3', 300),
            ('vitamin D', 'Описание 4', 400)
        ]
        cursor.executemany('INSERT INTO Products(title, description, price) VALUES (?, ?, ?)', products)

    # Создание таблицы Users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        age INTEGER NOT NULL,
        balance INTEGER NOT NULL DEFAULT 1000
    )
    ''')

    connection.commit()
    connection.close()

def add_user(username, email, age):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute('INSERT INTO Users(username, email, age, balance) VALUES (?, ?, ?, ?)', (username, email, age, 1000))
    connection.commit()
    connection.close()

def is_included(username):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Users WHERE username = ?', (username,))
    check_user = cursor.fetchone()
    connection.close()
    return check_user is not None  # Возвращаем True, если пользователь найден

def get_all_products():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("SELECT id, title, description, price FROM Products")
    products = cursor.fetchall()
    connection.close()
    return products  # Вернем список продуктов

# Инициализация базы данных и создание таблиц
initiate_db()

