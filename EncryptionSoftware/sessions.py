from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from log_new_session import LogNew
import sys


class Sessions(QMainWindow):
    def __init__(self, parent=None):
        super(Sessions, self).__init__(parent)
        self.setObjectName("MainWindow")
        self.resize(400, 250)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.pb_new_session = QtWidgets.QPushButton(self.centralwidget)
        self.pb_new_session.setGeometry(QtCore.QRect(120, 40, 141, 41))
        self.pb_new_session.setObjectName("pb_new_session")
        self.pb_join_session = QtWidgets.QPushButton(self.centralwidget)
        self.pb_join_session.setGeometry(QtCore.QRect(120, 120, 141, 41))
        self.pb_join_session.setObjectName("pb_join_session")
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 400, 21))
        self.menubar.setObjectName("menubar")
        self.menuAbout = QtWidgets.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuAbout.menuAction())

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        self.add_functions()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "Encryption software"))
        self.pb_new_session.setText(_translate("MainWindow", "Make new session"))
        self.pb_join_session.setText(_translate("MainWindow", "Join session"))
        self.menuAbout.setTitle(_translate("MainWindow", "About"))

    def add_functions(self):
        self.pb_new_session.clicked.connect(lambda: self.join_new_session())
        self.pb_join_session.clicked.connect(lambda: self.join_new_session())

    def join_new_session(self):
        session = LogNew(self)
        session.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Sessions()
    window.show()
    sys.exit(app.exec_())
