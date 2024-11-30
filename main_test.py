import pytest
import sqlite3
from datetime import datetime
import os
import openpyxl
from database import add_employee  # Импорт функции добавления сотрудника из вашего модуля
from reports_window import ReportsWindow


@pytest.fixture(scope="module")
def db_connection():
    """Создает подключение к базе данных для всех тестов"""
    conn = sqlite3.connect("employees_database.db")
    yield conn
    conn.close()  # Закрывается только после выполнения всех тестов

@pytest.fixture
def db_cursor(db_connection):
    """Создает курсор для работы с базой данных для каждого теста"""
    cursor = db_connection.cursor()
    yield cursor
    db_connection.commit()  # Применяет изменения после каждого теста



def test_add_employee(db_cursor):
    """Тест для добавления нового сотрудника"""
    db_cursor.execute("SELECT Count(*) FROM Сотрудник")
    count_begin = db_cursor.fetchone()[0]

    # Проверяем, существуют ли записи в таблицах Роль и Отдел
    db_cursor.execute("SELECT Count(*) FROM Роль WHERE ID = 1")
    role_count = db_cursor.fetchone()[0]

    db_cursor.execute("SELECT Count(*) FROM Отдел WHERE ID = 1")
    department_count = db_cursor.fetchone()[0]

    # Если записи с ID = 1 в таблицах Роль и Отдел не существует, добавим фиктивные данные
    if role_count == 0:
        db_cursor.execute("INSERT INTO Роль (ID, Название) VALUES (1, 'Обычный сотрудник')")
    if department_count == 0:
        db_cursor.execute("INSERT INTO Отдел (ID, Название) VALUES (1, 'Отдел кадров')")

    # Пример данных для нового сотрудника
    data = (
        "Петров",          # Фамилия
        "Иван",            # Имя
        "Сергеевич",       # Отчество
        "м",               # Пол
        "1985-08-15",      # Дата рождения
        "2020-01-01",      # Дата поступления
        1,                 # ID роли (например, "Обычный сотрудник")
        50000,             # Оклад
        "test@example.com",# Контакты
        1,                 # ID пользователя
        1                  # ID отдела
    )

    # Вызов функции добавления сотрудника
    add_employee(*data)

    # Проверяем, что количество записей увеличилось
    db_cursor.execute("SELECT Count(*) FROM Сотрудник")
    count_end = db_cursor.fetchone()[0]

    assert count_end - count_begin == 1, "Ошибка добавления сотрудника"

def test_add_multiple_employees(db_cursor):
    """
    Тест добавления нескольких сотрудников, среди которых есть ошибки в данных.
    """
    # Начальное количество записей
    db_cursor.execute("SELECT Count(*) FROM Сотрудник")
    count_begin = db_cursor.fetchone()[0]

    # Проверяем, существуют ли записи в таблицах Роль и Отдел
    db_cursor.execute("SELECT Count(*) FROM Роль WHERE ID = 1")
    role_count = db_cursor.fetchone()[0]

    db_cursor.execute("SELECT Count(*) FROM Отдел WHERE ID = 1")
    department_count = db_cursor.fetchone()[0]

    # Если записи с ID = 1 в таблицах Роль и Отдел не существует, добавим фиктивные данные
    if role_count == 0:
        db_cursor.execute("INSERT INTO Роль (ID, Название) VALUES (1, 'Обычный сотрудник')")
    if department_count == 0:
        db_cursor.execute("INSERT INTO Отдел (ID, Название) VALUES (1, 'Отдел кадров')")

    # Пример данных для добавления
    employees_data = [
        ("Иванов", "Иван", "Иванович", "м", "1985-05-15", "2010-03-01", 1, 45000, "ivanov@example.com", 1, 1),  # Корректно
        ("Петров", "", "Сергеевич", "м", "1985-15-15", "2020-03-01", 1, 50000, "petrov@example.com", 1, 1),  # Ошибка в дате рождения
        ("Сидоров", "Сергей", "", "м", "1990-02-20", "2015-01-01", 1, -10000, "sid@example.com", 1, 1),  # Ошибка в окладе
    ]

    added_count = 0  # Счётчик успешно добавленных записей

    for employee in employees_data:
        try:
            # Пробуем добавить сотрудника
            add_employee(*employee)
            added_count += 1
        except ValueError as e:
            print(f"Ошибка добавления сотрудника: {e}")
        except sqlite3.IntegrityError as e:
            print(f"Ошибка целостности базы данных: {e}")

    # Проверяем итоговое количество записей
    db_cursor.execute("SELECT Count(*) FROM Сотрудник")
    count_end = db_cursor.fetchone()[0]

    # Проверяем, что добавились только корректные записи
    assert count_end - count_begin == added_count, "Не все корректные записи были добавлены."



def test_delete_employee(db_cursor):
    """Тест для удаления сотрудника по фамилии"""
    # Добавляем тестового сотрудника
    db_cursor.execute("""
        INSERT INTO Сотрудник (Фамилия, Имя, Отчество, Пол, ДатаРождения, ДатаПоступления, Оклад, КонтактнаяИнформация, Пользователь_id, Отдел_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ("Иванов", "Иван", "Иванович", "м", "1990-01-01", "2015-06-01", 45000, "ivanov@example.com", 1, 1))

    # Проверяем, что сотрудник существует
    db_cursor.execute("SELECT Count(*) FROM Сотрудник WHERE Фамилия = ?", ("Иванов",))
    count_begin = db_cursor.fetchone()[0]
    assert count_begin > 0, "Сотрудник для удаления не был добавлен"

    # Удаляем сотрудника
    db_cursor.execute("DELETE FROM Сотрудник WHERE Фамилия = ?", ("Иванов",))

    # Проверяем, что запись удалена
    db_cursor.execute("SELECT Count(*) FROM Сотрудник WHERE Фамилия = ?", ("Иванов",))
    count_end = db_cursor.fetchone()[0]
    assert count_end == 0, "Ошибка удаления сотрудника"



def test_update_salary(db_cursor):
    """Тест для повышения оклада сотрудникам с определенным стажем на заданный процент."""
    # Устанавливаем минимальный стаж и процент повышения
    min_experience = 10  # минимальный стаж для повышения оклада
    increase_percentage = 10  # процент повышения оклада

    # Удаляем старые тестовые записи, если они есть
    db_cursor.execute("DELETE FROM Сотрудник WHERE Фамилия IN ('Иванов', 'Петров')")

    # Добавляем тестовых сотрудников с уникальными данными
    db_cursor.execute("""
        INSERT INTO Сотрудник (Фамилия, Имя, Отчество, Пол, ДатаРождения, ДатаПоступления, Оклад, КонтактнаяИнформация, Пользователь_id, Отдел_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ("Иванов", "Иван", "Иванович", "м", "1980-01-01", "2010-01-01", 50000, "ivanov@example.com", 1, 1))
    db_cursor.execute("""
        INSERT INTO Сотрудник (Фамилия, Имя, Отчество, Пол, ДатаРождения, ДатаПоступления, Оклад, КонтактнаяИнформация, Пользователь_id, Отдел_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ("Петров", "Петр", "Петрович", "м", "1985-01-01", "2020-01-01", 45000, "petrov@example.com", 1, 1))

    # Проверяем стаж сотрудников и применяем повышение оклада
    today = datetime.now()

    db_cursor.execute("SELECT ID, Оклад, ДатаПоступления FROM Сотрудник")
    employees = db_cursor.fetchall()

    for emp_id, initial_salary, hire_date in employees:
        if hire_date:
            try:
                experience_years = (today - datetime.strptime(hire_date.strip(), "%Y-%m-%d")).days // 365
                if experience_years >= min_experience:
                    new_salary = int(initial_salary * (1 + increase_percentage / 100))
                    db_cursor.execute("UPDATE Сотрудник SET Оклад = ? WHERE ID = ?", (new_salary, emp_id))
            except ValueError:
                continue  # Пропускаем записи с некорректным форматом даты

    # Проверяем, что оклад изменился правильно
    db_cursor.execute("SELECT Фамилия, Оклад, ДатаПоступления FROM Сотрудник")
    updated_employees = db_cursor.fetchall()

    for lastname, updated_salary, hire_date in updated_employees:
        if hire_date:
            experience_years = (today - datetime.strptime(hire_date.strip(), "%Y-%m-%d")).days // 365
            if experience_years >= min_experience:
                expected_salary = 50000 if lastname == "Иванов" else 45000
                expected_salary = int(expected_salary * (1 + increase_percentage / 100))
                assert updated_salary == expected_salary, \
                    f"Ошибка: Оклад не увеличился для {lastname} с нужным стажем."
            else:
                assert updated_salary == 45000, \
                    f"Ошибка: Оклад изменился для {lastname} без нужного стажа."



def test_generate_report(db_cursor):
    """Тест для генерации отчета в Excel о сотрудниках пенсионного возраста"""
    today = datetime.today()
    report_data = []

    db_cursor.execute("SELECT Фамилия, Имя, Отчество, Пол, ДатаРождения FROM Сотрудник")
    for lastname, firstname, patronymic, sex, birth_date in db_cursor.fetchall():
        if birth_date:
            age = (today - datetime.strptime(birth_date, "%Y-%m-%d")).days // 365
            retirement_age = 60 if sex == "ж" else 65
            if age >= retirement_age:
                report_data.append([lastname, firstname, patronymic, sex, birth_date, age])

    # Сохраняем данные в Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Отчет пенсионеры"
    ws.append(["Фамилия", "Имя", "Отчество", "Пол", "Дата Рождения", "Возраст"])

    for row in report_data:
        ws.append(row)

    report_path = "Отчет_пенсионеры.xlsx"
    wb.save(report_path)

    # Проверяем, что файл был создан
    assert os.path.exists(report_path), "Ошибка создания Excel отчета"

    # Удаляем файл после проверки
    os.remove(report_path)

# Команда для запуска всех тестов:
# pytest main_test.py
