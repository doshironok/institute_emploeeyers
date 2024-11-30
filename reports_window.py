from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox, QFileDialog, QComboBox, QInputDialog, QTableWidget, QTableWidgetItem
from datetime import datetime
import sqlite3
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from PyQt5.QtGui import QFont


class ReportsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Отчеты")
        self.setGeometry(250, 250, 800, 600)

        layout = QVBoxLayout()

        self.label = QLabel("Выберите тип отчета:")
        layout.addWidget(self.label)

        # Комбобокс для выбора типа отчета
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems(["Сотрудники пенсионного возраста", "Сотрудники с окладом ниже заданного"])
        layout.addWidget(self.report_type_combo)

        self.result_button = QPushButton("Сформировать отчет")
        self.result_button.clicked.connect(self.generate_report)
        layout.addWidget(self.result_button)

        # Таблица для отображения отчета
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(0)
        self.report_table.setRowCount(0)
        layout.addWidget(self.report_table)

        self.save_button = QPushButton("Сохранить в Excel")
        self.save_button.clicked.connect(self.save_to_excel)
        layout.addWidget(self.save_button)

        self.adjust_button = QPushButton("Повысить оклад")
        self.adjust_button.clicked.connect(self.adjust_salaries)
        layout.addWidget(self.adjust_button)

        self.delete_pensioners_button = QPushButton("Удалить пенсионеров")
        self.delete_pensioners_button.clicked.connect(self.delete_pensioners)
        layout.addWidget(self.delete_pensioners_button)

        self.setLayout(layout)
        self.report_data = []
        self.current_report_type = None

    def generate_report(self):
        report_type = self.report_type_combo.currentText()
        self.current_report_type = report_type
        today = datetime.today()
        self.report_data = []  # Очистить предыдущие данные отчета

        try:
            with sqlite3.connect("employees_database.db") as conn:
                cursor = conn.cursor()

                if report_type == "Сотрудники пенсионного возраста":
                    cursor.execute("SELECT Фамилия, Имя, Отчество, Пол, ДатаРождения, ДатаПоступления FROM Сотрудник")
                    self.report_data = [
                        (lastname, firstname, patronymic, sex, date_of_birth, date_of_start)
                        for lastname, firstname, patronymic, sex, date_of_birth, date_of_start in cursor.fetchall()
                        if date_of_birth and (datetime.strptime(date_of_birth, "%Y-%m-%d").year + (60 if sex == "ж" else 65)) <= today.year
                    ]
                    headers = ["Фамилия", "Имя", "Отчество", "Пол", "Дата Рождения", "Дата Поступления"]

                elif report_type == "Сотрудники с окладом ниже заданного":
                    min_salary, ok = QInputDialog.getInt(self, "Минимальный оклад", "Введите размер оклада:")
                    if not ok:
                        return

                    cursor.execute("SELECT Фамилия, Имя, Отчество, Оклад, ДатаПоступления FROM Сотрудник WHERE Оклад < ?", (min_salary,))
                    self.report_data = cursor.fetchall()
                    headers = ["Фамилия", "Имя", "Отчество", "Оклад", "Дата Поступления"]

                # Заполняем таблицу
                self.report_table.setRowCount(len(self.report_data))
                self.report_table.setColumnCount(len(headers))
                self.report_table.setHorizontalHeaderLabels(headers)

                for row_idx, row_data in enumerate(self.report_data):
                    for col_idx, col_data in enumerate(row_data):
                        self.report_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка при формировании отчета: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")

    def save_to_excel(self):
        if not self.report_data:
            QMessageBox.warning(self, "Ошибка", "Нет данных для сохранения.")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет в Excel", "",
                                                   "Excel Files (*.xlsx);;All Files (*)", options=options)

        if not file_path:
            return

        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Отчет"

            # Заголовки столбцов
            headers = [self.report_table.horizontalHeaderItem(col).text() for col in range(self.report_table.columnCount())]
            ws.append(headers)

            for cell in ws[1]:
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center')

            for row_idx in range(self.report_table.rowCount()):
                row_data = [
                    self.report_table.item(row_idx, col_idx).text() if self.report_table.item(row_idx, col_idx) else ""
                    for col_idx in range(self.report_table.columnCount())
                ]
                ws.append(row_data)

            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'

            wb.save(file_path)
            QMessageBox.information(self, "Успех", f"Отчет успешно сохранен в файле '{file_path}'.")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить отчет: {e}")

    def adjust_salaries(self):
        if not self.report_data or self.current_report_type != "Сотрудники с окладом ниже заданного":
            QMessageBox.warning(self, "Ошибка", "Нет данных для повышения оклада.")
            return

        min_experience, ok_exp = QInputDialog.getInt(self, "Стаж работы", "Введите минимальный стаж для повышения оклада:")
        if not ok_exp:
            return

        percentage, ok_percent = QInputDialog.getDouble(self, "Процент повышения", "Введите процент повышения оклада:",
                                                        decimals=2)
        if not ok_percent:
            return

        try:
            with sqlite3.connect("employees_database.db") as conn:
                cursor = conn.cursor()
                for row in self.report_data:
                    lastname, firstname, patronymic, salary, date_of_start = row
                    if date_of_start:
                        experience_years = (datetime.now() - datetime.strptime(date_of_start, "%Y-%m-%d")).days // 365
                        if experience_years >= min_experience:
                            new_salary = int(salary * (1 + percentage / 100))
                            cursor.execute("UPDATE Сотрудник SET Оклад = ? WHERE Фамилия = ? AND Имя = ? AND Отчество = ?",
                                           (new_salary, lastname, firstname, patronymic))

                conn.commit()
                QMessageBox.information(self, "Успех", f"Оклад успешно повышен на {percentage}% сотрудникам с опытом работы более {min_experience} лет.")
                self.generate_report()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка при обновлении окладов: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")

    def delete_pensioners(self):
        """Удаляет сотрудников пенсионного возраста из базы данных."""
        try:
            today = datetime.today()
            with sqlite3.connect("employees_database.db") as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    DELETE FROM Сотрудник
                    WHERE (
                        (Пол = 'ж' AND (strftime('%Y', 'now') - strftime('%Y', ДатаРождения)) >= 60)
                        OR
                        (Пол = 'м' AND (strftime('%Y', 'now') - strftime('%Y', ДатаРождения)) >= 65)
                    )
                """)

                deleted_count = cursor.rowcount  # Количество удаленных записей
                conn.commit()

                QMessageBox.information(
                    self,
                    "Успех",
                    f"Удалено {deleted_count} сотрудников пенсионного возраста."
                )
                self.generate_report()  # Обновляем отчет после удаления
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось удалить пенсионеров: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
