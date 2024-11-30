from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
                             QMessageBox, QSpacerItem, QSizePolicy, QHBoxLayout)
from PyQt5.QtCore import Qt
import hashlib
import sqlite3


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setGeometry(100, 200, 400, 330)  # Увеличим размеры окна
        self.setFixedWidth(400)
        self.setFixedHeight(330)

        # Основной layout
        main_layout = QVBoxLayout()

        # --- Добавляем изображение ---
        label = QLabel(self)
        pixmap = QPixmap('kubstu_logo.png')
        pixmap = pixmap.scaled(100, 100)  # Изменяем размер изображения
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)  # Центрируем изображение

        # Добавляем изображение в основной layout
        main_layout.addWidget(label)

        # Добавляем отступ между изображением и полями
        main_layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # --- Поля для ввода логина и пароля ---
        self.user_role = None
        self.user_id = None

        # Поле для ввода логина
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Логин")
        self.input_user.setFont(QFont("Segoe UI", 9))  # Увеличиваем шрифт
        self.input_user.setFixedHeight(35)  # Увеличиваем высоту поля
        self.input_user.setFixedWidth(300)

        user_layout = QHBoxLayout()
        user_layout.addStretch()
        user_layout.addWidget(self.input_user)
        user_layout.addStretch()

        # Поле для ввода пароля
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Пароль")
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setFont(QFont("Segoe UI", 9))  # Увеличиваем шрифт
        self.input_password.setFixedHeight(35)  # Увеличиваем высоту поля
        self.input_password.setFixedWidth(300)

        password_layout = QHBoxLayout()
        password_layout.addStretch()
        password_layout.addWidget(self.input_password)
        password_layout.addStretch()



        # Добавляем поля в основной layout
        main_layout.addLayout(user_layout)
        main_layout.addLayout(password_layout)

        # Кнопка входа
        self.login_button = QPushButton("Войти")
        self.login_button.setFont(QFont("Segoe UI", 9))
        self.login_button.setFixedHeight(40)
        self.login_button.setFixedWidth(100)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.login_button)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        self.login_button.clicked.connect(self.check_login)

        # Добавляем отступ перед кнопкой
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        main_layout.addWidget(self.login_button)
        main_layout.addStretch()

        # Устанавливаем основной layout для окна
        self.setLayout(main_layout)

    def check_login(self):
        username = self.input_user.text()
        password = self.input_password.text()
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Подключение к базе данных и проверка логина
        conn = sqlite3.connect("employees_database.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ID, Логин, (SELECT Название FROM Роль WHERE ID = Пользователь.ID) "
            "FROM Пользователь WHERE Логин = ? AND Пароль = ?",
            (username, password_hash)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            self.user_id = user[0]
            self.user_role = user[2]
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неправильное имя пользователя или пароль")


# Пример использования окна
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
