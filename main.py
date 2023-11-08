import sys
import sqlite3
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QPushButton

# для разрешения
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

# подключаем нашу базу данных
db = sqlite3.connect('bd.sqlite')
cursor = db.cursor()


class Income(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("income.ui", self)
        self.add_button.setText("Добавить в список")
        self.add_button.clicked.connect(self.add_data)

        self.income_button.setText("Доходы")
        self.expenses_button.setText("Расходы")
        self.distribution_button.setText("Распределение")

        self.load_data_to_table()

    def msg_box(self, elem):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText(elem)
        msgBox.setWindowTitle("Оповещение")
        msgBox.exec()

    def add_data(self):
        summ_value = float(self.amount_input.text())
        name_value = self.income_input.text()

        try:
            cursor.execute("INSERT INTO money_income (summ, name) VALUES (?, ?)",
                           (summ_value, name_value))
            db.commit()
            self.amount_input.clear()
            self.income_input.clear()
            self.msg_box("Данные успешно добавлены в базу данных.")
            self.load_data_to_table()
        except sqlite3.Error as e:
            self.msg_box(f"Ошибка: {str(e)}")

    def load_data_to_table(self):
        self.table_income.clear()

        try:
            cursor.execute("SELECT id, summ, name FROM money_income")
            data = cursor.fetchall()

            self.table_income.setRowCount(len(data))
            self.table_income.setColumnCount(5)  # 5 столбцов: ID, Summ, Name, Редактировать, Удалить
            self.table_income.setHorizontalHeaderLabels(["ID", "Summ", "Name", "Редактировать", "Удалить"])

            for row, row_data in enumerate(data):
                for column, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.table_income.setItem(row, column, item)

                # Добавим кнопку "Редактировать" в предпоследний столбец
                edit_button = QPushButton("Изменить")
                self.table_income.setCellWidget(row, 3, edit_button)

                # Добавим кнопку "Удалить" в последний столбец
                delete_button = QPushButton("Удалить")
                self.table_income.setCellWidget(row, 4, delete_button)

                # Подключим обработчики событий для кнопок "Удалить" и "Изменить"
                delete_button.clicked.connect(lambda _: self.delete_row(row))
                edit_button.clicked.connect(lambda _: self.edit_row(row))

        except sqlite3.Error as e:
            self.msg_box(f"Ошибка: {str(e)}")

    def delete_row(self, row):
        # Получите ID выбранной строки из таблицы
        item = self.table_income.item(row, 0)
        if item:
            id_to_delete = int(item.text())
            try:
                # Удалите строку из базы данных по ID
                cursor.execute("DELETE FROM money_income WHERE id = ?", (id_to_delete,))
                db.commit()
                self.load_data_to_table()  # Обновите таблицу
            except sqlite3.Error as e:
                self.msg_box(f"Ошибка при удалении: {str(e)}")
        else:
            self.msg_box("Выберите строку для удаления.")

    def edit_row(self, row):
        # Получите ID выбранной строки из таблицы
        item = self.table_income.item(row, 0)
        if item:
            id_to_edit = int(item.text())

            # Получите новые значения для обновления
            new_summ = float(self.table_income.item(row, 1).text())
            new_name = self.table_income.item(row, 2).text()

            try:
                # Обновите строку в базе данных по ID
                cursor.execute("UPDATE money_income SET summ = ?, name = ? WHERE id = ?",
                               (new_summ, new_name, id_to_edit))
                db.commit()
                self.load_data_to_table()  # Обновите таблицу
            except sqlite3.Error as e:
                self.msg_box(f"Ошибка при обновлении: {str(e)}")
        else:
            self.msg_box("Выберите строку для редактирования.")


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Income()
    window.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
