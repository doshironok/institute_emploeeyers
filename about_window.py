from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtGui import QFont, QPixmap
import os


class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("О программе")
        self.setGeometry(300, 300, 770, 600)
        self.setFixedWidth(770)
        self.setFixedHeight(600)
        # Шрифт для текста
        label_font = QFont("Segoe UI", 10)

        # Основной layout
        layout = QVBoxLayout()

        # Добавляем изображение
        image_label = QLabel(self)
        pixmap = QPixmap('about.jpg')
        pixmap = pixmap.scaled(770, 330)  # Масштабируем изображение до нужного размера
        image_label.setPixmap(pixmap)
        image_label.setFixedSize(770, 330)
        image_label.setStyleSheet("margin: 0 auto;")  # Центрируем изображение

        # Текстовая информация
        title_label = QLabel("Название программы: Программное средство для учёта сотрудников института")
        title_label.setFont(label_font)

        version_label = QLabel("Версия: 1.0.1")
        version_label.setFont(label_font)

        developer_label = QLabel("Разработчик: Зубенко Диана Сергеевна, 2024")
        developer_label.setFont(label_font)

        purpose_label = QLabel(
            "Назначение: Данное программное обеспечение разработано с целью использования сотрудниками "
            "отдела кадров института/университета при работе с сотрудниками."
        )
        purpose_label.setFont(label_font)
        purpose_label.setWordWrap(True)  # Перенос текста

        # Кнопка "Ок" для закрытия окна
        ok_button = QPushButton("Ок")
        ok_button.clicked.connect(self.close)

        # Добавляем элементы в layout
        layout.addWidget(image_label)
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addWidget(developer_label)
        layout.addWidget(purpose_label)
        layout.addWidget(ok_button)

        # Применяем layout
        self.setLayout(layout)
