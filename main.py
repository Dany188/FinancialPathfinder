# импорт нужных библиотек
import os
import sys
import sqlite3
import time
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QPushButton

# для разрешения
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

# подключаем нашу базу данных
db = sqlite3.connect('bd.sqlite')
cursor = db.cursor()


# Форма для работы с доходами
class Income(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("income.ui", self)
        self.setWindowIcon(QIcon(os.path.abspath('ico.ico')))


        self.add_button.setText("Добавить в список")
        self.add_button.clicked.connect(self.add_data)

        self.income_input.setPlaceholderText("Введите источник")
        self.amount_input.setPlaceholderText("Введите сумму")

        self.income_button.setText("Доходы")
        self.expenses_button.setText("Расходы")
        self.distribution_button.setText("Распределение")

        self.expenses_button.clicked.connect(self.income2expenses)
        self.distribution_button.clicked.connect(self.income2distribution)

        self.load_data_to_table()
        self.read_file()

    # Переход на форму с работой расходами
    def income2expenses(self):
        self.toexpenses = Expenses()
        self.toexpenses.show()
        self.hide()

    # Переход на форму с работой распределением
    def income2distribution(self):
        self.todistribution = Distribution()
        self.todistribution.show()
        self.hide()

    # Функция для вывода отдельного окна
    def msg_box(self, elem):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowIcon(QIcon('ico.ico'))
        msgBox.setText(elem)
        msgBox.setWindowTitle("Оповещение")
        msgBox.exec()

    # Читает txt файл и выводит сколько раз запускалось приложение
    def read_file(self):
        rfile = open('counter.txt', 'r', encoding="utf-8")
        self.b = rfile.read()
        rfile.close()
        if ('12' in str(self.b)) or ('13' in str(self.b)) or ('14' in str(self.b)):
            self.count1.setText(f'Приложение было запущено {int(self.b)} раз.')
        elif str(self.b)[-1] == '2' or str(self.b)[-1] == '3' or str(self.b)[-1] == '4':
            self.count1.setText(f'Приложение было запущено {int(self.b)} раза.')
        else:
            self.count1.setText(f'Приложение было запущено {int(self.b)} раз.')
        wfile = open('counter.txt', 'w', encoding="utf-8")
        wfile.write(str(self.b))
        wfile.close()

    # Загружает данные из бд в таблицу
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

    # Добавление в таблицу и бд
    def add_data(self):
        summ_value = self.amount_input.text()
        name_value = self.income_input.text()

        # Проверка если ничего не введено, но была нажата кнопка
        if not summ_value or not name_value:
            self.msg_box("Введите сумму и наименование дохода.")
            return

        # Проверка введенного значения
        try:
            float(summ_value)
        except ValueError:
            self.msg_box("Введите корректное числовое значение.")
            self.amount_input.clear()
            self.income_input.clear()
            return

        try:
            cursor.execute("INSERT INTO money_income (summ, name) VALUES (?, ?)",
                           (float(summ_value), name_value))
            db.commit()
            self.amount_input.clear()
            self.income_input.clear()
            self.msg_box("Данные успешно добавлены в базу данных.")
            self.load_data_to_table()
        except sqlite3.Error as e:
            self.msg_box(f"Ошибка: {str(e)}")

    # Удаление строки из таблицы и бд
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

    # Изменение строки и в бд
    def edit_row(self, row):
        # Получите ID выбранной строки из таблицы
        item = self.table_income.item(row, 0)
        if item:
            id_to_edit = int(item.text())

            # Получите новые значения для обновления
            try:
                new_summ = float(self.table_income.item(row, 1).text())
            except ValueError:
                self.msg_box("Введите корректное числовое значение в столбец 'summ'.")
                self.load_data_to_table()
                return
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

    # закрытие приложения
    def closeEvent(self, event):
        # При закрытии формы закроем и наше соединение
        # с базой данных
        db.close()
        # При закрытии формы закроем перепишем наш файл
        rfile = open('counter.txt', 'r', encoding="utf-8")
        b = rfile.read()
        rfile.close()
        c = int(b) + 1
        wfile = open('counter.txt', 'w', encoding="utf-8")
        wfile.write(str(c))
        wfile.close()


# Форма для работы с расходами
class Expenses(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("expenses.ui", self)
        self.setWindowIcon(QIcon('ico.ico'))

        self.add_button.setText("Добавить в список")
        self.add_button.clicked.connect(self.add_data)

        self.income_input.setPlaceholderText("Например: квартира, еда")
        self.amount_input.setPlaceholderText("Введите сумму")

        self.income_button.setText("Доходы")
        self.expenses_button.setText("Расходы")
        self.distribution_button.setText("Распределение")

        self.income_button.clicked.connect(self.expenses2income)
        self.distribution_button.clicked.connect(self.expenses2distribution)

        self.load_data_to_table()
        self.read_file()

    # Переход на форму с работой доходами
    def expenses2income(self):
        self.toincome = Income()
        self.toincome.show()
        self.hide()

    # Переход на форму с работой распределением
    def expenses2distribution(self):
        self.todistribution = Distribution()
        self.todistribution.show()
        self.hide()

    # Функция для вывода отдельного окна
    def msg_box(self, elem):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowIcon(QIcon('ico.ico'))
        msgBox.setText(elem)
        msgBox.setWindowTitle("Оповещение")
        msgBox.exec()

    # читает txt файл и выводит сколько раз запускалось приложение
    def read_file(self):
        rfile = open('counter.txt', 'r', encoding="utf-8")
        self.b = rfile.read()
        rfile.close()
        if ('12' in str(self.b)) or ('13' in str(self.b)) or ('14' in str(self.b)):
            self.count1.setText(f'Приложение было запущено {int(self.b)} раз.')
        elif str(self.b)[-1] == '2' or str(self.b)[-1] == '3' or str(self.b)[-1] == '4':
            self.count1.setText(f'Приложение было запущено {int(self.b)} раза.')
        else:
            self.count1.setText(f'Приложение было запущено {int(self.b)} раз.')
        wfile = open('counter.txt', 'w', encoding="utf-8")
        wfile.write(str(self.b))
        wfile.close()

    # Загружает данные из бд в таблицу
    def load_data_to_table(self):
        self.table_expenses.clear()

        try:
            cursor.execute("SELECT id, summ, name FROM money_expenses")
            data = cursor.fetchall()

            # Настройка таблицы
            self.table_expenses.setRowCount(len(data))
            self.table_expenses.setColumnCount(5)  # 5 столбцов: ID, Summ, Name, Редактировать, Удалить
            self.table_expenses.setHorizontalHeaderLabels(["ID", "Summ", "Name", "Редактировать", "Удалить"])

            for row, row_data in enumerate(data):
                for column, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.table_expenses.setItem(row, column, item)

                # Добавим кнопку "Редактировать" в предпоследний столбец
                edit_button = QPushButton("Изменить")
                self.table_expenses.setCellWidget(row, 3, edit_button)

                # Добавим кнопку "Удалить" в последний столбец
                delete_button = QPushButton("Удалить")
                self.table_expenses.setCellWidget(row, 4, delete_button)

                # Подключим обработчики событий для кнопок "Удалить" и "Изменить"
                delete_button.clicked.connect(lambda _: self.delete_row(row))
                edit_button.clicked.connect(lambda _: self.edit_row(row))

        except sqlite3.Error as e:
            self.msg_box(f"Ошибка: {str(e)}")

    # Добавление в таблицу и бд
    def add_data(self):
        summ_value = self.amount_input.text()
        name_value = self.income_input.text()

        # если ничего не введено, но кнопка была нажата
        if not summ_value or not name_value:
            self.msg_box("Введите сумму и наименование дохода.")
            return

        # Проверка какое значение было введено в лайн эдит
        try:
            float(summ_value)
        except ValueError:
            self.msg_box("Введите корректное числовое значение.")
            self.amount_input.clear()
            self.income_input.clear()
            return

        try:
            cursor.execute("INSERT INTO money_expenses (summ, name) VALUES (?, ?)",
                           (float(summ_value), name_value))
            db.commit()
            self.amount_input.clear()
            self.income_input.clear()
            self.msg_box("Данные успешно добавлены в базу данных.")
            self.load_data_to_table()
        except sqlite3.Error as e:
            self.msg_box(f"Ошибка: {str(e)}")

    # Удаление строки из таблицы и бд
    def delete_row(self, row):
        # Получите ID выбранной строки из таблицы
        item = self.table_expenses.item(row, 0)
        if item:
            id_to_delete = int(item.text())
            try:
                # Удалите строку из базы данных по ID
                cursor.execute("DELETE FROM money_expenses WHERE id = ?", (id_to_delete,))
                db.commit()
                self.load_data_to_table()  # Обновите таблицу
            except sqlite3.Error as e:
                self.msg_box(f"Ошибка при удалении: {str(e)}")
        else:
            self.msg_box("Выберите строку для удаления.")

    # Изменение строки в таблице и бд
    def edit_row(self, row):
        # Получите ID выбранной строки из таблицы
        item = self.table_expenses.item(row, 0)
        if item:
            id_to_edit = int(item.text())

            # Проверка введенного значения на float
            try:
                new_summ = float(self.table_expenses.item(row, 1).text())
            except ValueError:
                self.msg_box("Введите корректное числовое значение в столбец 'summ'.")
                self.load_data_to_table()
                return
            new_name = self.table_expenses.item(row, 2).text()

            try:
                # Обновите строку в базе данных по ID
                cursor.execute("UPDATE money_expenses SET summ = ?, name = ? WHERE id = ?",
                               (new_summ, new_name, id_to_edit))
                db.commit()
                self.load_data_to_table()  # Обновите таблицу
            except sqlite3.Error as e:
                self.msg_box(f"Ошибка при обновлении: {str(e)}")
        else:
            self.msg_box("Выберите строку для редактирования.")

    # закрытие приложения
    def closeEvent(self, event):
        # При закрытии формы закроем и наше соединение
        # с базой данных
        db.close()
        # При закрытии формы закроем перепишем наш файл
        rfile = open('counter.txt', 'r', encoding="utf-8")
        b = rfile.read()
        rfile.close()
        c = int(b) + 1
        wfile = open('counter.txt', 'w', encoding="utf-8")
        wfile.write(str(c))
        wfile.close()


# Форма для работы с распределением
class Distribution(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("distribution.ui", self)
        self.setWindowIcon(QIcon('ico.ico'))

        self.income_button.setText("Доходы")
        self.expenses_button.setText("Расходы")
        self.distribution_button.setText("Распределение")

        self.income_button.clicked.connect(self.distribution2income)
        self.expenses_button.clicked.connect(self.distribution2expenses)

        self.calculate_distribution()
        self.read_file()
        self.progress_bar()

    # Переход на форму с работой доходами
    def distribution2income(self):
        self.toincome = Income()
        self.toincome.show()
        self.hide()

    # Переход на форму с работой расходами
    def distribution2expenses(self):
        self.toexpenses = Expenses()
        self.toexpenses.show()
        self.hide()

    # читает txt файл и выводит сколько раз запускалось приложение
    def read_file(self):
        rfile = open('counter.txt', 'r', encoding="utf-8")
        self.b = rfile.read()
        rfile.close()
        if ('12' in str(self.b)) or ('13' in str(self.b)) or ('14' in str(self.b)):
            self.count1.setText(f'Приложение было запущено {int(self.b)} раз.')
        elif str(self.b)[-1] == '2' or str(self.b)[-1] == '3' or str(self.b)[-1] == '4':
            self.count1.setText(f'Приложение было запущено {int(self.b)} раза.')
        else:
            self.count1.setText(f'Приложение было запущено {int(self.b)} раз.')
        wfile = open('counter.txt', 'w', encoding="utf-8")
        wfile.write(str(self.b))
        wfile.close()

    # изменение шкалы прогресса пользователя
    def progress_bar(self):
        # Получить общий доход и общие расходы из базы данных
        cursor.execute("SELECT SUM(summ) FROM money_income")
        total_income = cursor.fetchone()[0]

        # цикл для медленного заполнения бара
        cursor.execute("SELECT SUM(summ) FROM money_expenses")
        total_expenses = cursor.fetchone()[0]
        for i in range(int((total_expenses / total_income) * 100)):
            number = self.progress.value()
            self.progress.setValue(number + 1)
            time.sleep(0.0001)

    # Подсчет данных для таблицы
    def calculate_distribution(self):
        self.table_distribution.clear()

        try:
            # Получить общий доход и общие расходы из базы данных
            cursor.execute("SELECT SUM(summ) FROM money_income")
            total_income = cursor.fetchone()[0]

            cursor.execute("SELECT SUM(summ) FROM money_expenses")
            total_expenses = cursor.fetchone()[0]

            # Рассчитаем распределение
            total_available = total_income - total_expenses
            usd = total_available * 0.20
            eur = total_available * 0.20
            stocks = total_available * 0.20
            crypto = total_available * 0.10
            travel = total_available * 0.05
            free_money = total_available * 0.25

            # Заполняем table_distribution вычисленными значениями
            self.table_distribution.setRowCount(1)
            self.table_distribution.setColumnCount(7)
            self.table_distribution.setHorizontalHeaderLabels(
                ["Общий доход", "USD", "EUR", "Акции", "Криптовалюта", "Путешествия", "Свободные деньги"]
            )

            # Установка значение в ячейки
            self.table_distribution.setItem(0, 0, QTableWidgetItem(str(total_available)))
            self.table_distribution.setItem(0, 1, QTableWidgetItem(str(usd)))
            self.table_distribution.setItem(0, 2, QTableWidgetItem(str(eur)))
            self.table_distribution.setItem(0, 3, QTableWidgetItem(str(stocks)))
            self.table_distribution.setItem(0, 4, QTableWidgetItem(str(crypto)))
            self.table_distribution.setItem(0, 5, QTableWidgetItem(str(travel)))
            self.table_distribution.setItem(0, 6, QTableWidgetItem(str(free_money)))

        except sqlite3.Error as e:
            self.msg_box(f"Ошибка: {str(e)}")

    # закрытие приложения
    def closeEvent(self, event):
        # При закрытии формы закроем и наше соединение
        # с базой данных
        db.close()
        # При закрытии формы закроем перепишем наш файл
        rfile = open('counter.txt', 'r', encoding="utf-8")
        b = rfile.read()
        rfile.close()
        c = int(b) + 1
        wfile = open('counter.txt', 'w', encoding="utf-8")
        wfile.write(str(c))
        wfile.close()


# для обработки ошибок
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Income()
    window.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
