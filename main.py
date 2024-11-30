import sys
from PyQt5.QtWidgets import QApplication
from login_window import LoginWindow
from main_window import MainWindow

# Запуск приложения
app = QApplication(sys.argv)

# Окно авторизации
login_window = LoginWindow()

if login_window.exec_() == LoginWindow.Accepted:
    user_role = login_window.user_role  # Получаем роль пользователя
    user_id = login_window.user_id      # Получаем ID пользователя
    main_window = MainWindow(user_role, user_id)  # Передаем роль и ID в главное окно
    main_window.show()
    sys.exit(app.exec_())
