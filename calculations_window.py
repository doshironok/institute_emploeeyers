from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QComboBox, QTextEdit
import sqlite3
from PyQt5.QtGui import QFont

class CalculationsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Расчеты")
        self.setGeometry(200, 200, 500, 500)

        layout = QVBoxLayout()

        # Заголовок и выбор действия
        self.label_action = QLabel("Выберите действие:")
        self.label_action.setFont(QFont("Segoe UI", 11))

        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "Стаж работы всех сотрудников",
            "Средний стаж работы сотрудников заданного отдела",
            "Количество сотрудников с окладом ниже заданного"
        ])
        self.action_combo.currentIndexChanged.connect(self.toggle_inputs)

        self.department_combo = QComboBox()
        self.load_departments()
        self.department_combo.setVisible(False)

        self.wage_input = QLineEdit()
        self.wage_input.setPlaceholderText("Введите размер оклада")
        self.wage_input.setVisible(False)

        self.result_button = QPushButton("Выполнить расчет")
        self.result_button.clicked.connect(self.calculate)

        self.result_output = QTextEdit()
        self.result_output.setFont(QFont("Segoe UI", 10))
        self.result_output.setReadOnly(True)

        layout.addWidget(self.label_action)
        layout.addWidget(self.action_combo)
        layout.addWidget(QLabel("Выберите отдел:"))
        layout.addWidget(self.department_combo)
        layout.addWidget(self.wage_input)
        layout.addWidget(self.result_button)
        layout.addWidget(self.result_output)

        self.setLayout(layout)

    def load_departments(self):
        conn = sqlite3.connect("employees_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT Название FROM Отдел")
        departments = cursor.fetchall()
        conn.close()

        self.department_combo.addItem("Выберите отдел")
        for department in departments:
            self.department_combo.addItem(department[0])

    def toggle_inputs(self):
        selected_action = self.action_combo.currentText()
        if selected_action == "Средний стаж работы сотрудников заданного отдела":
            self.department_combo.setVisible(True)
            self.wage_input.setVisible(False)
        elif selected_action == "Количество сотрудников с окладом ниже заданного":
            self.department_combo.setVisible(False)
            self.wage_input.setVisible(True)
        else:
            self.department_combo.setVisible(False)
            self.wage_input.setVisible(False)

    def calculate(self):
        action = self.action_combo.currentText()
        conn = sqlite3.connect("employees_database.db")
        cursor = conn.cursor()

        result_text = ""
        if action == "Стаж работы всех сотрудников":
            cursor.execute("SELECT Фамилия, Имя, СтажРаботы FROM Сотрудник")
            rows = cursor.fetchall()
            for lastname, name, exp in rows:
                result_text += f"{lastname} {name}: {exp} лет стажа\n"

        elif action == "Средний стаж работы сотрудников заданного отдела":
            department = self.department_combo.currentText()
            if department == "Выберите отдел":
                result_text = "Ошибка: Выберите корректный отдел."
            else:
                cursor.execute(
                    "SELECT СтажРаботы, Фамилия, Имя FROM Сотрудник WHERE Отдел_id = (SELECT ID FROM Отдел WHERE Название = ?)",
                    (department,))
                rows = cursor.fetchall()
                exp_list = [exp for exp, _, _ in rows]
                avg_experience = sum(exp_list) / len(exp_list) if exp_list else 0
                result_text = f"Средний стаж сотрудников отдела '{department}': {avg_experience:.2f} лет\n"
                for exp, lastname, name in rows:
                    result_text += f"{lastname} {name}: {exp} лет стажа\n"

        elif action == "Количество сотрудников с окладом ниже заданного":
            try:
                wage = int(self.wage_input.text())
                cursor.execute("SELECT Фамилия, Имя, Оклад FROM Сотрудник WHERE Оклад < ?", (wage,))
                rows = cursor.fetchall()
                result_text = f"Количество сотрудников с окладом ниже {wage}: {len(rows)}\n"
                for lastname, name, wage in rows:
                    result_text += f"{lastname} {name}: {wage} руб.\n"
            except ValueError:
                result_text = "Ошибка: Введите корректное значение оклада."

        self.result_output.setText(result_text)
        conn.close()
