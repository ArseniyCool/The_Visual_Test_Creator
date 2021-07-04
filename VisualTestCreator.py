import sys
import sqlite3
import functools
import winsound
import PyQt5

from functools import partial
from PyQt5 import uic, QtTest
from PyQt5.QtSql import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton,\
    QWidget, QScrollArea, QFrame, QTableView
from PyQt5.QtWidgets import QMainWindow, QGroupBox, QFormLayout

WHITE = 'rgb(255, 255, 255)'
BLACK = 'rgb(0, 0, 0)'
COLOR = ['rgb(215, 255, 165)', 'rgb(178, 255, 89)', 'rgb(115, 236, 38)', 'rgb(100, 221, 23)',
         'rgb(255, 82, 82)', 'rgb(255, 23, 68)', 'rgb(255, 245, 0)']
# TODO: 2 ФАЗА (База данных, исправление недочетов, дизайн)
#  -СДЕЛАНО- Неизменяемый размер окон, регистрация, отдельный фрейм для окон "регистрация", "тест" и
#   и "результат"




class HelpWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('help.ui', self)
        self.setWindowTitle("HELP")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F3:
            MyWidget().help_close()



class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Design of test.ui', self)
        self.setWindowTitle('Design of test New')
        self.pause_now = False
        self.reg = False
        self.help = False
        self.first_init = True
        self.buttons_setup()
        self.setup_registration()

    def buttons_setup(self):
        # Белая панель
        self.help_btn.clicked.connect(self.help_open)
        # Регистрация
        self.enter_btn.clicked.connect(self.check_registration)
        # Пауза
        self.btn_special.clicked.connect(self.pause_event)
        self.continue_test.clicked.connect(self.test_event)
        self.start_again.clicked.connect(partial(self.test_event, True))
        self.exit_btn.clicked.connect(exit)
        # Тест
        self.drop.clicked.connect(self.dropping)
        self.backward.clicked.connect(self.backward_event)
        self.ready.clicked.connect(self.save_test_to_continue)
        # Результат
        self.users_btn.clicked.connect(partial(self.init_sqltable, 'top_users'))
        self.test_results_btn.clicked.connect(partial(self.init_sqltable, 'test_results'))
        self.exit_btn_2.clicked.connect(exit)

    def help_close(self):
        self.w.hide()

    def help_open(self):
        self.w = HelpWidget()
        self.w.show()

    def setup_registration(self):
        self.frame_result.setVisible(False)
        self.frame_reg.setVisible(True)
        self.frame_test.setVisible(False)
        self.frame_pause.setVisible(False)
        self.btn_special.setEnabled(False)
        self.name_input.setPlaceholderText("  Вася Пупкин")
        self.email_input.setPlaceholderText("  vasya_pupkin@mail.ru")
        self.setFixedSize(640, 490)
        self.error.setVisible(False)
        self.x = self.error.pos().x()
        self.y = self.error.pos().y()

    def check_registration(self):
        self.name = str(self.name_input.text())
        self.email = str(self.email_input.text())
        self.age = int(self.age_input.text())
        con = sqlite3.connect('app_users.db')
        cur = con.cursor()
        self.base_emails = cur.execute("""SELECT email FROM users""").fetchall()
        con.close()
        if not self.email.endswith('@mail.ru') \
            or (self.age == 0 or self.name.strip() == '' or self.email.strip() == '') \
                or self.email in self.base_emails:

            self.enter_btn.setEnabled(False)
            if self.age == 0 or self.name.strip() == '' or self.email.strip() == '':
                self.error.setText('      Заполнены не все поля!')
            elif self.email in self.base_emails:
                self.error.setText('       Этот email уже занят!')
            else:
                self.error.setText('        Некорректный email!')
            self.error.setVisible(True)
            x = 20
            for i in range(0, 12):
                self.error.move(x - self.error.size().width(), self.y)
                x += 20 + i * 2
                QtTest.QTest.qWait(10)
            QtTest.QTest.qWait(1200)
            for i in range(0, 12):
                self.error.move(x - self.error.size().width(), self.y)
                x += 20 + i * 2
                QtTest.QTest.qWait(10)
            self.error.setVisible(False)
            self.enter_btn.setEnabled(True)
        else:
            self.test_event()

    def test_event(self, setup=False):
        self.btn_special.setEnabled(True)
        self.frame_pause.setVisible(True)
        self.stage = 1

        self.result_counts = []
        self.favourites_of_values = []

        self.pause_now = False
        self.frame_result.setVisible(False)
        self.frame_reg.setVisible(False)
        self.frame_pause.setVisible(False)
        self.frame_test.setVisible(True)
        self.frame_test.setEnabled(True)
        if setup:
            for i in range(20):
                self.setFixedSize(640, 810 - i * 16)
                QtTest.QTest.qWait(10)
            self.setup_tests()
        elif not self.reg:
            self.reg = True
            self.setup_tests()

    def setup_tests(self):
        self.ready.setStyleSheet(f'''background-color: rgb(171, 171, 171);
                                                 color: rgb(255, 255, 255);''')
        self.ready.setEnabled(True)

        self.drop.setStyleSheet(f'''background-color: rgb(171, 171, 171);
                                                color: rgb(255, 255, 255);''')
        self.drop.setEnabled(False)
        self.backward.setStyleSheet(f'''background-color: rgb(171, 171, 171);
                                                            color: rgb(255, 255, 255);''')
        self.backward.setEnabled(False)
        self.favourite_name = None
        con = sqlite3.connect('tests.db')

        # Создание курсора
        cur = con.cursor()
        self.test = cur.execute(f"""SELECT name FROM types_of_tests
                                 WHERE id = '{self.stage}'""").fetchall()[0][0]
        self.test_name.setText(f'ТЕСТ {self.stage} / 5 "РАЗВЛЕЧЕНИЯ : {self.test.upper()}"')
        self.f = cur.execute(f"""SELECT name FROM {self.test}""").fetchall()
        self.buttons = []
        self.counts = []
        self.nums = []
        self.favourite = True
        self.end = False

        self.push_need = round(0.3 * (5 * len(self.f) + 1))  # кол-во необходимых нажатий на кнопку
        # вычисляется по формуле: "процент_необходимых нажатий * максимально_возможное_кол-во_нажатий
        self.push_count = 0
        self.completed = 0

        self.test_info.setText(f'НАЖМИТЕ ЕЩЕ НА {self.push_need - self.push_count} КНОПОК')
        self.progress.setValue(self.completed)
        self.backward.setEnabled(False)
        self.ready.setEnabled(False)
        self.drop.setEnabled(False)
        self.test_name.setEnabled(False)
        self.last_number = 0
        self.last_index = 0
        self.num = 14
        formLayout = QFormLayout()
        groupBox = QGroupBox()
        for i in range(len(self.f)):
            # print(self.f[i][0])
            # if len(self.f[i][0]) > 16:
            #     self.num = 8
            self.button = QPushButton(self.f[i][0], self)
            # if len(self.f[i][0]) <= 4:
            #     self.num = 18
            # elif len(self.f[i][0]) <= 6:
            #     self.num = 14
            # elif len(self.f[i][0]) <= 8:
            #     self.num = 11
            # elif len(self.f[i][0]) <= 16:
            #     self.num = 9
            self.nums.append(self.num)
            self.button.setStyleSheet(f'''background-color: rgb(215, 255, 165);
                                         color: rgb(0, 0, 0);
                                         font: {self.num}pt "Sans Serif";
                                         border-radius: 30px 30px;''')
            self.button.clicked.connect(self.button_click)
            formLayout.addRow(self.button)
            self.counts.append(0)
            self.buttons.append(self.button)
        groupBox.setLayout(formLayout)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidget(groupBox)
        self.scrollArea.setWidgetResizable(True)
        self.show()
        if self.stage == 1:
            for i in range(40):
                self.scrollArea.move(10, -440 + i * 12)
                self.setFixedSize(640, 500 + i * 8)
                QtTest.QTest.qWait(10)
        else:
            for i in range(40):
                self.scrollArea.move(10, -440 + i * 12)
                QtTest.QTest.qWait(10)

    def save_test_to_continue(self):
        self.result_counts.append(self.counts)
        if self.favourite_name:
            self.favourites_of_values.append(self.favourite_name)
        else:
            self.favourites_of_values.append(None)
        self.stage += 1
        if self.stage <= 5:
            if self.stage == 5:
                self.ready.setText('ЗАКОНЧИТЬ ТЕСТ')
            self.setup_tests()
        else:
            self.ready_event()


    def pause_event(self):
        if self.pause_now:
            self.setFocusPolicy(Qt.StrongFocus)
            self.pause_now = False
            self.test_event()
        else:
            self.setFocusPolicy(Qt.StrongFocus)
            self.pause_now = True
            self.frame_result.setVisible(False)
            self.frame_reg.setVisible(False)
            self.frame_test.setEnabled(False)
            self.frame_pause.setVisible(True)
        # self.setFixedSize(640, 460)



    def button_click(self):
        sender = self.sender()
        index = self.buttons.index(sender)
        if self.end or (not self.favourite and 5 <= self.counts[index] <= 7):
            return
        else:
            self.push_count += 1
            self.completed = round((self.push_count / self.push_need) * 100)
            self.progress.setValue(self.completed)
            self.backward.setEnabled(True)
            self.backward.setStyleSheet(f'''background-color: rgb(68, 138, 255);
                                                        color: rgb(255, 255, 255);''')
        self.last_button = self.sender()
        self.last_index = index
        if self.push_need == self.push_count:
            self.test_info.setText('ГОТОВО')
            winsound.PlaySound('sounds/pushbutton.wav', winsound.SND_ASYNC)
            self.end = True
            self.ready.setEnabled(True)
            self.ready.setStyleSheet(f'''background-color: rgb(68, 138, 255);
                                                    color: rgb(255, 255, 255);''')
        else:
            self.test_info.setText(f'НАЖМИТЕ ЕЩЕ НА {self.push_need - self.push_count} КНОПОК')
        if self.counts[index] == 0:
            self.drop.setEnabled(True)
            self.drop.setStyleSheet(f'''background-color: rgb(68, 138, 255);
                                                color: rgb(255, 255, 255);''')
            MyWidget.usual_button_click(self, sender, index)
        elif self.counts[index] < 3:
            MyWidget.like_button_click(self, sender, index)
        elif self.counts[index] < 5:
            MyWidget.adore_button_click(self, sender, index)
        elif self.counts[index] == 5:
            if self.favourite:
                self.favourite = False
                winsound.PlaySound('sounds/pushbutton.wav', winsound.SND_ASYNC)
                MyWidget.favour_button_click(self, sender, index)
            else:
                return
        if self.counts[index] != 5:
            winsound.PlaySound('sounds/pushbutton.wav', winsound.SND_ASYNC)
            self.counts[index] += 1

    def usual_button_click(self, sender, index):
        self.last_number = 0
        sender.resize(70, 70)
        sender.move(sender.x() - 5, sender.y() - 5)
        sender.setStyleSheet(f'''background-color: rgb(178, 255, 89);
                                color: rgb(0, 0, 0);
                                font: {self.nums[index] + self.counts[index] + 1}pt "Sans Serif";
                                border-radius: 35px 35px;''')

    def like_button_click(self, sender, index):
        if self.counts[index] == 1:
            self.last_number = 1
            sender.resize(80, 80)
            sender.move(sender.x() - 5, sender.y() - 5)
            sender.setStyleSheet(f'''background-color: rgb(115, 236, 38);
                                    color: rgb(0, 0, 0);
                                    font: {self.nums[index] + self.counts[index] + 1}pt "Sans Serif";
                                    border-radius: 40px 40px;''')
        else:
            self.last_number = 2
            sender.resize(90, 90)
            sender.move(sender.x() - 5, sender.y() - 5)
            sender.setStyleSheet(f'''background-color: rgb(100, 221, 23);
                                    color: rgb(0, 0, 0);
                                    font: {self.nums[index] + self.counts[index] + 1}pt "Sans Serif";
                                    border-radius: 45px 45px;''')

    def adore_button_click(self, sender, index):
        if self.counts[index] == 3:
            self.last_number = 3
            sender.resize(100, 100)
            sender.move(sender.x() - 5, sender.y() - 5)
            sender.setStyleSheet(f'''background-color: rgb(255, 82, 82);
                                    color: rgb(255, 255, 255);
                                    font: {self.nums[index] + self.counts[index] + 1}pt 
                                    "Sans Serif";
                                    border-radius: 50px 50px;''')
        else:
            self.last_number = 4
            sender.resize(110, 110)
            sender.move(sender.x() - 5, sender.y() - 5)
            sender.setStyleSheet(f'''background-color: rgb(255, 23, 68);
                                    color: rgb(255, 255, 255);
                                    font: {self.nums[index] + self.counts[index] + 1}pt 
                                    "Sans Serif";
                                    border-radius: 55px 55px;''')

    def favour_button_click(self, sender, index):
        self.last_number = 5
        self.counts[index] += 1
        sender.resize(120, 120)
        sender.move(sender.x() - 5, sender.y() - 5)
        sender.setStyleSheet(f'''background-color: rgb(255, 245, 0);
                                color: rgb(0, 0, 0);
                               font: {self.nums[index] + self.counts[index] + 1}pt "Sans Serif";
                                border-radius: 60px 60px;''')
        self.favourite_name = sender.text()

    def dropping(self):
        if self.end:
            self.ready.setStyleSheet(f'''background-color: rgb(171, 171, 171);
                                         color: rgb(255, 255, 255);''')
            self.ready.setEnabled(True)
        self.drop.setStyleSheet(f'''background-color: rgb(171, 171, 171);
                                    color: rgb(255, 255, 255);''')
        self.drop.setEnabled(False)
        self.backward.setStyleSheet(f'''background-color: rgb(171, 171, 171);
                                                color: rgb(255, 255, 255);''')
        self.backward.setEnabled(False)
        self.last_number = 0
        self.end = False
        self.favourite = True
        self.push_count = 0
        self.completed = 0
        self.test_info.setText(f'НАЖМИТЕ ЕЩЕ НА {self.push_need - self.push_count} КНОПОК')
        self.progress.setValue(self.completed)
        # x, y, = 70, 70
        self.num = 14
        for i in range(len(self.f)):
            self.button = self.buttons[i]
        #     if len(self.f[i]) <= 4:
        #         self.num = 18
        #     elif len(self.f[i]) <= 6:
        #         self.num = 14
        #     elif len(self.f[i]) <= 8:
        #         self.num = 11
        #     elif len(self.f[i]) <= 15:
        #         self.num = 9
        #     else:
        #         self.num = 5
        #     self.nums[i] = self.num
            self.button.setStyleSheet(f'''background-color: rgb(215, 255, 165); 
                                         color: rgb(0, 0, 0);
                                         font: {self.num}pt "Sans Serif";
                                         border-radius: 30px 30px;''')
            self.counts[i] = 0

    def backward_event(self):
        if self.end:
            self.ready.setStyleSheet(f'''background-color: rgb(171, 171, 171);
                                         color: rgb(255, 255, 255);''')
            self.ready.setEnabled(False)
            self.end = False
        self.push_count -= 1
        self.completed = round((self.push_count / self.push_need) * 100)
        self.test_info.setText(f'НАЖМИТЕ ЕЩЕ НА {self.push_need - self.push_count} КНОПОК')
        self.progress.setValue(self.completed)
        if self.push_count == 0:
            self.drop.setStyleSheet(f'''background-color: rgb(171, 171, 171);
                                        color: rgb(255, 255, 255);''')
            self.drop.setEnabled(False)

        text_color = WHITE if 3 < self.last_number <= 5 else BLACK
        if self.last_number == 5:
            self.favourite = True
            self.counts[self.last_index] += 1
        self.last_button.resize(self.last_number * 10 + 60, self.last_number * 10 + 60)
        self.last_button.move(self.last_button.x() + 5, self.last_button.y() + 5)
        self.last_button.setStyleSheet(f'''background-color: {COLOR[self.last_number]}; 
                                           color: {text_color};
                                           font: {self.nums[self.last_index] + self.last_number}pt "Sans Serif";
                                           border-radius: {self.last_number * 5 + 30}px {self.last_number * 5 + 30}px;''')
        self.backward.setEnabled(False)
        self.counts[self.last_index] -= 1
        self.backward.setStyleSheet(f'''background-color: rgb(171, 171, 171);
                                        color: rgb(255, 255, 255);''')

    def ready_event(self):
        self.frame_pause.setVisible(False)
        self.frame_result.setVisible(True)
        self.frame_reg.setVisible(False)
        self.frame_pause.setVisible(False)
        self.frame_test.setVisible(False)
        self.commit_user()
        self.commit_score()

    def commit_user(self):
        con = sqlite3.connect('app_users.db')
        cur = con.cursor()
        data = (self.name, self.email, self.age, self.favourites_of_values[0],
                self.favourites_of_values[1], self.favourites_of_values[2],
                self.favourites_of_values[3], self.favourites_of_values[4])
        try:
            cur.execute("""INSERT INTO users(name, email, age, music, game, attraction, movie, book) 
                                 VALUES (?,?,?,?,?,?,?,?)""", data)
        except sqlite3.Error:
            print("""Произошел fail! Приносим свои извинения за принесенные неудобства!
Попробуйте перезайти в приложение или обратитесь в техподдержку""")
        con.commit()
        con.close()


    def commit_score(self):
        con = sqlite3.connect('app_users.db')
        cur = con.cursor()
        for name in ['music', 'game', 'attraction', 'movie', 'book']:
            count_id = ['music', 'game', 'attraction', 'movie', 'book'].index(name)
            id_of_score = name + '_id'
            name_of_score = name + '_score'
            summa1 = sum(map(lambda x: x[0], cur.execute(f"""SELECT score FROM {name_of_score}""").fetchall()))
            summa2 = sum(map(int, self.result_counts[count_id]))
            summa = summa1 + summa2
            for i in range(len(self.result_counts[count_id])):
                score = cur.execute(f"""SELECT score FROM {name_of_score}
                                                WHERE {id_of_score} = {i + 1}""").fetchall()[0][0] \
                        + self.result_counts[count_id][i]
                cur.execute(f"""UPDATE {name_of_score} SET score = {score}, 
                                        'procent, %' = {round((score / summa) * 100, 1)}
                                        WHERE {id_of_score} = {i + 1}""")
            con.commit()
        con.close()


    def init_sqltable(self, table_use='top_users'):
        if self.first_init:
            self.first_init = False
            for i in range(1, 20):
                self.tableView.setStyleSheet(f'''background-color: rgba(255, 255, 255, {0 + i * 0.05});''')
                QtTest.QTest.qWait(10)
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('app_users.db')
        db.open()

        model = QSqlTableModel(self, db)
        if table_use == 'top_users':
            table_name = 'users'
        else:
            table_name = ['music_score', 'game_score', 'attraction_score',
                          'movie_score', 'book_score'][int(self.spinBox.value()) - 1]
        model.setTable(table_name)
        model.select()

        self.tableView.setModel(model)



    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F5:
            if self.reg:
                self.test_event(True)
        if int(event.modifiers()) == Qt.ShiftModifier:
            if event.key() == Qt.Key_Escape:
                exit()
        elif event.key() == Qt.Key_F3:
            self.help_open()
        elif event.key() == Qt.Key_Space:
            if self.reg:
                if self.pause_now:
                    self.test_event()
                else:
                    self.pause_event()
            elif not self.reg:
                self.check_registration()
        elif event.key() == Qt.Key_Escape:
            if self.reg:
                if self.pause_now:
                    self.test_event()
                else:
                    self.pause_event()



try:
    if __name__ == '__main__':
        app = QApplication(sys.argv)
        ex = MyWidget()
        ex.show()
        sys.exit(app.exec_())
except Exception as error:
    print(error)
