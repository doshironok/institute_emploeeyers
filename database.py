import sqlite3
import hashlib
from datetime import datetime

# Подключение к базе данных
conn = sqlite3.connect("employees_database.db")
cursor = conn.cursor()

# Создание таблицы сотрудников
cursor.execute('''CREATE TABLE IF NOT EXISTS Сотрудник (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Фамилия TEXT NOT NULL,
    Имя TEXT NOT NULL,
    Отчество TEXT,
    Пол TEXT,
    ДатаРождения DATE,
    ДатаПоступления DATE,
    Роль_id INTEGER,
    СтажРаботы INTEGER,
    Оклад INTEGER,
    КонтактнаяИнформация TEXT,
    Пользователь_id INTEGER,
    Отдел_id INTEGER,
    FOREIGN KEY (Должность_id) REFERENCES Роль(ID),
    FOREIGN KEY (Пользователь_id) REFERENCES Пользователь(ID),
    FOREIGN KEY (Отдел_id) REFERENCES Отдел(ID)
)''')

# Создание таблицы отделов
cursor.execute('''CREATE TABLE IF NOT EXISTS Отдел (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Название TEXT NOT NULL,
    Руководитель_id INTEGER,
    FOREIGN KEY (Руководитель_id) REFERENCES Сотрудник(ID)
)''')

# Создание таблицы вакансий
cursor.execute('''CREATE TABLE IF NOT EXISTS Вакансия (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Должность_id INTEGER,
    Оклад INTEGER,
    Отдел_id INTEGER,
    FOREIGN KEY (Должность_id) REFERENCES Роль(ID),
    FOREIGN KEY (Отдел_id) REFERENCES Отдел(ID)
)''')

# Создание таблицы пользователей
cursor.execute('''CREATE TABLE IF NOT EXISTS Пользователь (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Логин TEXT NOT NULL UNIQUE,
    Пароль TEXT NOT NULL
)''')

# Создание таблицы ролей
cursor.execute('''CREATE TABLE IF NOT EXISTS Роль (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Название TEXT NOT NULL,
    Права TEXT
)''')

conn.commit()


# Функции для управления профилями и наймом сотрудников

# Функция для добавления нового пользователя (логин и хешированный пароль)
def add_user(login, password):
    # Проверяем, существует ли логин в базе данных
    cursor.execute("SELECT ID FROM Пользователь WHERE Логин = ?", (login,))
    user = cursor.fetchone()

    if user:
        print(f"Пользователь с логином '{login}' уже существует. Обновление пароля.")
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("UPDATE Пользователь SET Пароль = ? WHERE Логин = ?", (password_hash, login))
    else:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT INTO Пользователь (Логин, Пароль) VALUES (?, ?)", (login, password_hash))

    conn.commit()
    return cursor.lastrowid if not user else user[0]


# Функция для добавления роли сотрудника
def add_role(name, rights):
    cursor.execute("INSERT INTO Роль (Название, Права) VALUES (?, ?)", (name, rights))
    conn.commit()
    return cursor.lastrowid


def add_employee(lastname, name, patronimic, sex, date_of_birth, date_of_start, role_id, wage,
                 contacts, user_id, department_id):
    """Добавляет нового сотрудника в таблицу 'Сотрудник'"""
    # Проверяем корректность даты
    try:
        datetime.strptime(date_of_birth, "%Y-%m-%d")
        datetime.strptime(date_of_start, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Некорректный формат даты")

    # Проверяем оклад
    if wage <= 0:
        raise ValueError("Оклад должен быть положительным числом")

    # Проверяем, что все поля заполнены
    if not all([lastname, name, sex, date_of_birth, date_of_start, role_id, wage, contacts, user_id, department_id]):
        raise ValueError("Все поля должны быть заполнены")

    # Подключение к базе данных
    conn = sqlite3.connect("employees_database.db")
    cursor = conn.cursor()

    try:
        # Вычисляем стаж работы
        exp = (datetime.now() - datetime.strptime(date_of_start, "%Y-%m-%d")).days // 365

        # Добавляем запись в таблицу
        cursor.execute('''
            INSERT INTO Сотрудник 
            (Фамилия, Имя, Отчество, Пол, ДатаРождения, ДатаПоступления, Роль_id, СтажРаботы, Оклад, КонтактнаяИнформация, Пользователь_id, Отдел_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (lastname, name, patronimic, sex, date_of_birth, date_of_start, role_id, exp, wage,
              contacts, user_id, department_id))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()



def update_employee_experience():
    """Обновляет стаж работы сотрудников на основе текущей даты."""

    today = datetime.now()
    cursor.execute("SELECT ID, ДатаПоступления FROM Сотрудник")
    rows = cursor.fetchall()

    for employee_id, date_of_start in rows:
        if date_of_start is None:
            print(f"Дата поступления не указана для сотрудника с ID {employee_id}. Пропуск обновления стажа.")
            continue  # Пропускаем сотрудников без даты поступления

        date_of_start = date_of_start.strip()
        experience_years = (today - datetime.strptime(date_of_start, "%Y-%m-%d")).days // 365
        cursor.execute("UPDATE Сотрудник SET СтажРаботы = ? WHERE ID = ?", (experience_years, employee_id))

    conn.commit()
    conn.close()


# Пример добавления новой роли, пользователя и сотрудника в систему

def hire_employee(lastname, name, patronimic, sex, date_of_birth, date_of_start,  wage,
                        contacts, login, password, role_name, rights, departament_id):
    # Добавляем роль
    if role_name == "Сотрудник отдела кадров":
        role_id = 2
    elif role_name == "Обычный сотрудник":
        role_id = 1
    else:
        role_id = add_role(role_name, rights)

    # Добавляем пользователя с логином и паролем
    user_id = add_user(login, password)

    # Добавляем сотрудника с профилем и данными учетной записи
    employee_id = add_employee(
        lastname, name, patronimic, sex, date_of_birth, date_of_start,
        role_id=role_id, wage=wage, contacts=contacts,
        user_id=user_id, department_id=departament_id
    )

    print(f"Сотрудник {lastname} {name} добавлен в систему с ID: {employee_id}")


# Пример данных для нового сотрудника
lastname = "Петров"
name = "Иван"
patronimic = "Сергеевич"
sex = "м"
date_of_birth = "1985-08-15"
date_of_start = "2024-01-01"
wage = 45000
contacts = "ivan.petrov@example.com"
login = "petrov_ivan"
password = "securepassword123"
#position_name = "Обычный сотрудник"
position_name = "Сотрудник отдела кадров"
rights = "Просмотр профиля, Запросы на отпуск/пенсию/декрет"
departament_id = 1  # ID отдела, в котором будет работать сотрудник

# Функция для авторизации пользователя
def auth(login, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT ID, Логин FROM Пользователь WHERE Логин = ? AND Пароль = ?", (login, password_hash))
    user = cursor.fetchone()

    if user:
        print(f"Вход успешен для пользователя: {user[1]}")
        return user[0]  # Возвращаем ID пользователя для сессии
    else:
        print("Неверный логин или пароль")
        return None


# Проверка авторизации
user_id = auth("petrov_ivan", "securepassword123")
if user_id:
    print("Авторизация прошла успешно.")
else:
    print("Ошибка авторизации.")


# Обновляем стаж для всех сотрудников при запуске
update_employee_experience()

# Подключение к базе данных
conn = sqlite3.connect("employees_database.db")
cursor = conn.cursor()

# Пример данных для нового пользователя отдела кадров
login = "hr_manager"
password = "hrpassword123"
user_role = "Сотрудник отдела кадров"
rights = "Полный доступ к таблице сотрудников, расчетам, отчетам, управлению вакансиями"

# Добавляем роль
#role_id = add_role(user_role, rights)

# Добавляем пользователя с логином и паролем, привязанного к роли
user_id = add_user(login, password)

print(f"Пользователь отдела кадров добавлен в систему с логином '{login}'.")



# Закрытие соединения с базой данных
conn.close()
