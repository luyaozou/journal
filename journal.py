#! encoding = utf-8

""" Keep journal
One journal one day keeps the doctor away
"""

import json
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from os.path import isfile, realpath, dirname
from os.path import join as path_join
from datetime import datetime, timedelta
import sys


JOURNAL_FILE = path_join(dirname(realpath(__file__)), 'zou_journal.json')
CONFIG_FILE = path_join(dirname(realpath(__file__)), 'config')


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.setStyleSheet('font-size: 12pt')
        self.setMinimumWidth(300)
        self.setMinimumHeight(400)
        self.resize(QtCore.QSize(600, 800))
        self.setWindowIcon(QIcon('icon_planner.png'))

        t = datetime.now()
        today = t.strftime('%Y-%m-%d')
        self._today = today
        self.journal_file = ""
        self.journal_data = {}
        if isfile(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as fp:
                self.journal_file = fp.readline().strip()
                self._load()
        else:
            with open(CONFIG_FILE, 'w') as fp:
                fp.write('\n')

        self.labelDate = QtWidgets.QLabel()
        self.labelTime = QtWidgets.QLabel()
        self.labelDate.setStyleSheet('font-size: 16pt')
        self.labelTime.setStyleSheet('font-size: 16pt')
        self.labelDate.setAlignment(QtCore.Qt.AlignHCenter)
        self.labelTime.setAlignment(QtCore.Qt.AlignHCenter)

        self.btnSave = QtWidgets.QPushButton('保存')
        self.btnSave.setFixedWidth(100)
        self.btnSave.clicked.connect(self._save_txt)
        # self.btnSave.layout().setAlignment(QtCore.Qt.AlignRight)
        self.editWin = QtWidgets.QTextEdit()
        area = QtWidgets.QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(self.editWin)
        # try load today's text
        if today in self.journal_data:
            self.editWin.setText(self.journal_data[today])

        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        thisLayout.addWidget(self.labelDate)
        thisLayout.addWidget(self.labelTime)
        thisLayout.addWidget(area)
        thisLayout.addWidget(self.btnSave)

        mainWidget = QtWidgets.QWidget()
        mainWidget.setLayout(thisLayout)
        self.setCentralWidget(mainWidget)

        self.dialogCalendar = DialogCalendar(parent=self)
        self.dialogJournal = DialogJournal(self.journal_data, parent=self)
        self.viewAction = QtWidgets.QAction('View Calendar', self)
        self.openAction = QtWidgets.QAction('Open File', self)
        self.openAction.setShortcut('Ctrl+O')
        self.saveAction = QtWidgets.QAction('Save', self)
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAsAction = QtWidgets.QAction('Save As', self)
        self.saveAsAction.setShortcut('Ctrl+Alt+S')
        menu = self.menuBar().addMenu('&File')
        menu.addAction(self.openAction)
        menu.addAction(self.saveAction)
        menu.addAction(self.saveAsAction)
        menu = self.menuBar().addMenu('&Calendar')
        menu.addAction(self.viewAction)
        self.viewAction.triggered.connect(self.dialogCalendar.show)
        self.openAction.triggered.connect(self.open_journal)
        self.saveAction.triggered.connect(self._save_file)
        self.saveAsAction.triggered.connect(self._save_file_as)
        self.dialogCalendar.accepted.connect(self.show_journal)

        # set up a timer
        self.update_date_time()
        self.clockTimer = QtCore.QTimer()
        self.clockTimer.setInterval(1000)
        self.clockTimer.setSingleShot(False)
        self.clockTimer.timeout.connect(self.update_date_time)
        self.clockTimer.start()

    def closeEvent(self, ev):
        self.btnSave.click()
        self.saveAction.trigger()
        if isfile(self.journal_file):
            # the file has been saved validly
            with open(CONFIG_FILE, 'w', encoding='utf-8') as fp:
                fp.write(self.journal_file)
            ev.accept()
        else:
            ev.ignore()

    def update_date_time(self):

        t = datetime.now()
        self.labelDate.setText(t.strftime('%Y %b %d, %A'))
        self.labelTime.setText(t.strftime('%p %I:%M:%S'))
        today = t.strftime('%Y-%m-%d')
        # check if today is still today
        if today != self._today:
            self._save()    # save journal to old date
            # clear input box
            self.editWin.clear()
            # update date
            self._today = today

    def _save_txt(self):
        txt = self.editWin.toPlainText()
        self.journal_data[self._today] = txt

    def _save_file(self):
        """ Save journal file """
        if self.journal_file:
            with open(self.journal_file, 'w', encoding='utf-8') as fp:
                json.dump(self.journal_data, fp, indent=2, ensure_ascii=False)
        else:
            self._save_file_as()

    def _save_file_as(self):
        f, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, 'Save As Journal File', dirname(realpath(__file__)),
                'Json File (*.json)')
        if f:
            with open(f, 'w', encoding='utf-8') as fp:
                json.dump(self.journal_data, fp, indent=2, ensure_ascii=False)
            self.journal_file = f
            self.setWindowTitle('Simple Journal: ' + self.journal_file)

    def _load(self):
        """ Load journal file, if file does not exist, create one """
        if isfile(self.journal_file):
            with open(self.journal_file, 'r', encoding='utf-8') as fp:
                self.journal_data = json.load(fp)
            self.setWindowTitle('Simple Journal: ' + self.journal_file)
        else:
            self.journal_data = {}
            self.setWindowTitle('Simple Journal (New File)')

    def open_journal(self):
        f, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, 'Open Journal File', dirname(realpath(__file__)),
                'Json File (*.json)')
        self.journal_file = f
        self._load()

    def show_journal(self):
        date_str = self.dialogCalendar.calendar.selectedDate().toString('yyyy-MM-dd')
        t = datetime.strptime(date_str, '%Y-%m-%d')
        self.dialogJournal.set_date(t)


class DialogCalendar(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('日历')
        self.calendar = QtWidgets.QCalendarWidget(parent)
        btn = QtWidgets.QPushButton('Select')
        btn.setFixedWidth(100)
        self.calendar.showToday()
        self.calendar.setFirstDayOfWeek(QtCore.Qt.Sunday)
        self.calendar.setSelectionMode(QtWidgets.QCalendarWidget.SingleSelection)

        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        thisLayout.addWidget(self.calendar)
        thisLayout.addWidget(btn)
        self.setLayout(thisLayout)
        btn.clicked.connect(self.accept)


class DialogJournal(QtWidgets.QDialog):

    def __init__(self, journal_data, parent=None):
        super().__init__(parent)
        self.resize(QtCore.QSize(600, 400))
        self.journal_data = journal_data
        self.btnPrev = QtWidgets.QPushButton('Prev')
        self.btnNext = QtWidgets.QPushButton('Next')
        self.btnPrev.setFixedWidth(150)
        self.btnNext.setFixedWidth(150)
        self.labelDate = QtWidgets.QLabel()
        self.labelDate.setAlignment(QtCore.Qt.AlignCenter)

        self.btnEdit = QtWidgets.QPushButton('Enable Edit')
        self.btnEdit.setFixedWidth(150)
        self.btnEdit.setCheckable(True)
        self.btnEdit.setChecked(False)
        self.btnEdit.toggled[bool].connect(self._change_edit_state)
        self.editJournal = QtWidgets.QTextEdit()
        self.editJournal.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.editJournal.setReadOnly(True)
        self.btnSave = QtWidgets.QPushButton('保存')
        self.btnSave.setDisabled(True)
        self.btnSave.setFixedWidth(150)
        self.btnSave.clicked.connect(self._save_txt)
        self.btnPrev.clicked.connect(self._prev)
        self.btnNext.clicked.connect(self._next)

        area = QtWidgets.QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(self.editJournal)

        thisLayout = QtWidgets.QGridLayout()
        thisLayout.setAlignment(QtCore.Qt.AlignTop)
        thisLayout.addWidget(self.btnPrev, 0, 0)
        thisLayout.addWidget(self.labelDate, 0, 1)
        thisLayout.addWidget(self.btnNext, 0, 2)
        thisLayout.addWidget(area, 1, 0, 1, 3)
        thisLayout.addWidget(self.btnEdit, 2, 0)
        thisLayout.addWidget(self.btnSave, 2, 2)
        self.setLayout(thisLayout)

    def _change_edit_state(self, b):
        self.btnEdit.setText('Disable Edit' if b else 'Enable Edit')
        self.editJournal.setReadOnly(not b)
        self.btnSave.setDisabled(not b)

    def _save_txt(self):
        txt = self.editJournal.toPlainText()
        self.journal_data[self.windowTitle()] = txt

    def set_date(self, t):
        date_str = t.strftime('%Y-%m-%d')
        self.setWindowTitle(date_str)
        self.labelDate.setText(t.strftime('%Y %b %d, %A'))
        if date_str in self.journal_data:
            self.editJournal.setText(self.journal_data[date_str])
        else:
            self.editJournal.setText('')
        self.showNormal()

    def _prev(self):
        t = datetime.strptime(self.windowTitle(), '%Y-%m-%d')
        self.set_date(t - timedelta(days=1))

    def _next(self):
        t = datetime.strptime(self.windowTitle(), '%Y-%m-%d')
        self.set_date(t + timedelta(days=1))

        
def launch():
   
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
    
    
if __name__ == '__main__':

    launch()
