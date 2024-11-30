from PyQt5.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QComboBox, QLabel, \
    QWidget, QHBoxLayout, QMessageBox, QInputDialog, QAction
from PyQt5.QtGui import QFont
import sqlite3
from profile_window import ProfileWindow
from calculations_window import CalculationsWindow
from reports_window import ReportsWindow
from about_window import AboutWindow  # Импортируем окно "О программе"


class MainWindow(QMainWindow):
    def __init__(self, user_role, user_id):
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.setWindowTitle("Система учета сотрудников")
        self.setGeometry(100, 100, 1200, 600)

        # Создаем верхнюю панель с кнопкой "О программе"
        self.create_top_menu()

        # Главный виджет и основной макет
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Левая панель с кнопками
        left_panel = QVBoxLayout()

        self.profile_button = QPushButton("Просмотр профиля")
        self.profile_button.clicked.connect(self.open_profile_window)

        self.calculations_button = QPushButton("Расчеты")
        self.calculations_button.clicked.connect(self.open_calculations_window)

        self.reports_button = QPushButton("Отчеты")
        self.reports_button.clicked.connect(self.open_reports_window)

        # Добавляем кнопки в левую панель
        left_panel.addWidget(self.profile_button)

        # Проверка прав доступа к расчетам и отчетам для сотрудников отдела кадров
        if self.user_role == "Сотрудник отдела кадров":
            left_panel.addWidget(self.calculations_button)
            left_panel.addWidget(self.reports_button)

        # Комбобокс для выбора таблицы и управление отображением данных
        self.table_selector = QComboBox()
        self.table_selector.addItems(["Сотрудники", "Отделы", "Роли"])
        self.table_selector.currentTextChanged.connect(self.load_table)

        # Создаем вертикальный layout для надписи и комбобокса
        table_selection_layout = QVBoxLayout()
        label = QLabel("Выберите таблицу для отображения:")
        table_selection_layout.addWidget(label)
        table_selection_layout.addWidget(self.table_selector)

        # Добавляем этот layout в основную левую панель
        left_panel.addLayout(table_selection_layout)

        # Кнопки для управления записями таблицы
        self.add_button = QPushButton("Добавить запись")
        self.add_button.clicked.connect(self.add_record)

        self.edit_button = QPushButton("Редактировать запись")
        self.edit_button.clicked.connect(self.edit_record)

        self.delete_button = QPushButton("Удалить запись")
        self.delete_button.clicked.connect(self.delete_record)

        left_panel.addWidget(self.add_button)
        left_panel.addWidget(self.edit_button)
        left_panel.addWidget(self.delete_button)

        # Таблица сотрудников (правая часть экрана)
        self.table_widget = QTableWidget()
        self.table_widget.setFont(QFont("Segoe UI", 11))
        self.table_widget.setSortingEnabled(True)

        # Добавляем левую панель и таблицу сотрудников в основной макет
        main_layout.addLayout(left_panel, 1)
        main_layout.addWidget(self.table_widget, 3)

        # Загружаем таблицу "Сотрудники" по умолчанию
        self.load_table("Сотрудники")

    def create_top_menu(self):
        """Создает верхнюю панель с кнопкой 'О программе'"""
        about_action = QAction("О программе", self)  # Создаем действие
        about_action.triggered.connect(self.open_about_window)  # Подключаем к действию метод открытия окна

        menu_bar = self.menuBar()  # Получаем верхнюю панель
        menu_bar.addAction(about_action)  # Добавляем кнопку "О программе"

    # Метод для загрузки данных в таблицу
    def load_table(self, table_name):
        with sqlite3.connect("employees_database.db") as conn:
            cursor = conn.cursor()
            self.current_table = table_name  # Сохраняем текущую таблицу

            if table_name == "Сотрудники":
                cursor.execute(
                    "SELECT ID, Фамилия, Имя, Пол, ДатаРождения, ДатаПоступления, Оклад, СтажРаботы FROM Сотрудник")
                rows = cursor.fetchall()
                headers = ["ID", "Фамилия", "Имя", "Пол", "Дата Рождения", "Дата Поступления", "Оклад", "Стаж"]

            elif table_name == "Отделы":
                cursor.execute("SELECT ID, Название FROM Отдел")
                rows = cursor.fetchall()
                headers = ["ID", "Название"]

            elif table_name == "Роли":
                cursor.execute("SELECT ID, Название, Права FROM Роль")
                rows = cursor.fetchall()
                headers = ["ID", "Название", "Права"]

            # Заполняем таблицу данными
            self.table_widget.setRowCount(len(rows))
            self.table_widget.setColumnCount(len(headers))
            self.table_widget.setHorizontalHeaderLabels(headers)

            for row_idx, row_data in enumerate(rows):
                for col_idx, col_data in enumerate(row_data):
                    self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

    # Открытие окна "О программе"
    def open_about_window(self):
        self.about_window = AboutWindow()
        self.about_window.show()

    # Открытие окна профиля
    def open_profile_window(self):
        self.profile_window = ProfileWindow(self.user_id)
        self.profile_window.show()

    # Открытие окна расчетов
    def open_calculations_window(self):
        self.calculations_window = CalculationsWindow()
        self.calculations_window.show()

    # Открытие окна отчетов
    def open_reports_window(self):
        self.reports_window = ReportsWindow()
        self.reports_window.show()


    # Метод для добавления записи
    def add_record(self):
        table = self.current_table
        try:
            with sqlite3.connect("employees_database.db") as conn:
                cursor = conn.cursor()

                if table == "Сотрудники":
                    # Ввод данных сотрудника через QInputDialog
                    lastname, ok1 = QInputDialog.getText(self, "Добавить запись", "Введите фамилию:")
                    name, ok2 = QInputDialog.getText(self, "Добавить запись", "Введите имя:")
                    gender, ok3 = QInputDialog.getText(self, "Добавить запись", "Введите пол:")
                    birthdate, ok4 = QInputDialog.getText(self, "Добавить запись",
                                                          "Введите дату рождения (гггг-мм-дд):")
                    hiredate, ok5 = QInputDialog.getText(self, "Добавить запись",
                                                         "Введите дату поступления (гггг-мм-дд):")
                    wage, ok6 = QInputDialog.getInt(self, "Добавить запись", "Введите оклад:")

                    if all([ok1, ok2, ok3, ok4, ok5, ok6]):
                        cursor.execute(
                            "INSERT INTO Сотрудник (Фамилия, Имя, Пол, ДатаРождения, ДатаПоступления, Оклад) VALUES (?, ?, ?, ?, ?, ?)",
                            (lastname, name, gender, birthdate, hiredate, wage)
                        )
                    else:
                        return  # Прерываем, если отменено хотя бы одно поле

                elif table == "Отделы":
                    department_name, ok = QInputDialog.getText(self, "Добавить запись", "Введите название отдела:")
                    if ok:
                        cursor.execute("INSERT INTO Отдел (Название) VALUES (?)", (department_name,))

                elif table == "Роли":
                    role_name, ok1 = QInputDialog.getText(self, "Добавить запись", "Введите название роли:")
                    rights, ok2 = QInputDialog.getText(self, "Добавить запись", "Введите права роли:")
                    if ok1 and ok2:
                        cursor.execute("INSERT INTO Роль (Название, Права) VALUES (?, ?)", (role_name, rights))

                conn.commit()
                self.load_table(table)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка базы данных: {e}")

    # Метод для редактирования записи
    def edit_record(self):
        table = self.current_table
        selected_row = self.table_widget.currentRow()
        selected_column = self.table_widget.currentColumn()

        if selected_row == -1 or selected_column == -1:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите запись и поле для редактирования.")
            return

        # Получаем ID записи из первой колонки (предполагаем, что ID всегда в первой колонке)
        record_id = self.table_widget.item(selected_row, 0).text()
        column_name = self.table_widget.horizontalHeaderItem(selected_column).text()  # Название столбца
        old_value = self.table_widget.item(selected_row, selected_column).text()  # Старое значение

        # Запрашиваем новое значение у пользователя
        new_value, ok = QInputDialog.getText(self, "Редактировать поле",
                                             f"Изменить '{column_name}' (текущее значение: {old_value}):")

        # Если пользователь нажал OK и ввел значение
        if ok and new_value:
            try:
                with sqlite3.connect("employees_database.db") as conn:
                    cursor = conn.cursor()

                    # Формируем SQL-запрос для обновления конкретного поля
                    if table == "Сотрудники":
                        cursor.execute(f"UPDATE Сотрудник SET {column_name} = ? WHERE ID = ?", (new_value, record_id))
                    elif table == "Отделы":
                        cursor.execute(f"UPDATE Отдел SET {column_name} = ? WHERE ID = ?", (new_value, record_id))
                    elif table == "Роли":
                        cursor.execute(f"UPDATE Роль SET {column_name} = ? WHERE ID = ?", (new_value, record_id))

                    conn.commit()
                    QMessageBox.information(self, "Успех", f"Поле '{column_name}' успешно обновлено.")

                # Обновляем значение в таблице интерфейса без перезагрузки всей таблицы
                self.table_widget.setItem(selected_row, selected_column, QTableWidgetItem(new_value))
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось обновить поле: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить операцию: {e}")
        else:
            QMessageBox.information(self, "Отмена", "Редактирование отменено.")
    # Метод для удаления записи
    def delete_record(self):
        table = self.current_table
        selected_row = self.table_widget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите запись для удаления.")
            return

        record_id = self.table_widget.item(selected_row, 0).text()
        reply = QMessageBox.question(self, "Удалить запись", "Вы уверены, что хотите удалить эту запись?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect("employees_database.db")
            cursor = conn.cursor()

            if table == "Сотрудники":
                cursor.execute("DELETE FROM Сотрудник WHERE ID = ?", (record_id,))
            elif table == "Отделы":
                cursor.execute("DELETE FROM Отдел WHERE ID = ?", (record_id,))
            elif table == "Роли":
                cursor.execute("DELETE FROM Роль WHERE ID = ?", (record_id,))

            conn.commit()
            conn.close()
            self.load_table(table)
