from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QTextEdit, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sqlite3


class ProfileWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("Профиль сотрудника")
        self.setGeometry(200, 200, 400, 400)  # Размер окна

        layout = QVBoxLayout()

        # Заголовок
        self.profile_label = QLabel("Информация о сотруднике:")
        self.profile_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.profile_label.setAlignment(Qt.AlignCenter)  # Центрируем заголовок

        # Поле для отображения информации о сотруднике (текстовое поле с прокруткой)
        self.info_text_edit = QTextEdit()
        self.info_text_edit.setFont(QFont("Segoe UI", 10))  # Меньший шрифт для информации
        self.info_text_edit.setReadOnly(True)  # Сделать поле только для чтения
        self.info_text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # Добавляем вертикальную прокрутку
        self.info_text_edit.setWordWrapMode(True)  # Разрешаем перенос строк

        # Добавляем отступ
        layout.addWidget(self.profile_label)
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addWidget(self.info_text_edit)

        self.setLayout(layout)

        self.load_profile()

    def load_profile(self):
        conn = sqlite3.connect("employees_database.db")
        cursor = conn.cursor()

        # Получаем данные сотрудника по user_id
        cursor.execute(
            "SELECT Фамилия, Имя, Отчество, Пол, ДатаРождения, ДатаПоступления, Оклад, СтажРаботы FROM Сотрудник WHERE Пользователь_id = ?",
            (self.user_id,))
        profile_data = cursor.fetchone()
        conn.close()

        if profile_data:
            profile_text = f"""
            Фамилия: {profile_data[0]}
            Имя: {profile_data[1]}
            Отчество: {profile_data[2]}
            Пол: {profile_data[3]}
            Дата Рождения: {profile_data[4]}
            Дата Поступления: {profile_data[5]}
            Оклад: {profile_data[6]} руб.
            Стаж: {profile_data[7]} лет
            """
            self.info_text_edit.setPlainText(profile_text)  # Устанавливаем текст в QTextEdit
        else:
            self.info_text_edit.setPlainText("Не удалось найти информацию о сотруднике.")
