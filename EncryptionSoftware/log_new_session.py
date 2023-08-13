import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from account import Account
import sys
import requests
from variables import SERVER_ADDRESS


class LogNew(QDialog):
    def __init__(self, parent=None):
        super(LogNew, self).__init__(parent)
        self.setObjectName("Dialog")
        self.resize(400, 250)
        self.pb_join = QtWidgets.QPushButton(self)
        self.pb_join.setGeometry(QtCore.QRect(250, 190, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.pb_join.setFont(font)
        self.pb_join.setObjectName("pb_join")
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(90, 100, 111, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.le_pass = QtWidgets.QLineEdit(self)
        self.le_pass.setGeometry(QtCore.QRect(90, 130, 170, 25))
        self.le_pass.setObjectName("le_pass")
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(90, 20, 71, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.le_login = QtWidgets.QLineEdit(self)
        self.le_login.setGeometry(QtCore.QRect(90, 50, 170, 25))
        self.le_login.setObjectName("le_login")

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        self.add_functions()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "ES login"))
        self.pb_join.setText(_translate("Dialog", "Join"))
        self.label.setText(_translate("Dialog", "Password"))
        self.label_2.setText(_translate("Dialog", "Login"))

    def add_functions(self):
        self.pb_join.clicked.connect(lambda: self.join_new_session(self.le_login.text(), self.le_pass.text()))

    def join_new_session(self, login: str, password: str):
        if login == '' or password == '':
            message = QMessageBox()
            message.setWindowTitle("Error connection")
            message.setText("You forgot to enter your username or password")
            message.setIcon(QMessageBox.Warning)
            message.exec_()
        else:
            try:
                resp = requests.post(f"{SERVER_ADDRESS}/login/{login}?password={password}")
                if resp.status_code == 200:
                    print(f"User logined: {resp.text}")
                    account = Account(login, resp.text, parent=self)
                    account.show()
                    self.close()
                elif resp.status_code == 201:
                    print(f"User created: {resp.text}")
                    if not os.path.exists(f'file_to_send/{resp.text}'):
                        os.makedirs(f'file_to_send/{resp.text}')
                    account = Account(login, resp.text, parent=self)
                    account.show()
                    self.close()
                else:
                    message = QMessageBox()
                    message.setWindowTitle("Error connection")
                    message.setText("Password is incorrect")
                    message.setIcon(QMessageBox.Warning)
                    message.exec_()
            except requests.ConnectionError:
                message = QMessageBox()
                message.setWindowTitle("Error connection")
                message.setText("Can not connect to server")
                message.setIcon(QMessageBox.Warning)
                message.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LogNew()
    window.show()
    sys.exit(app.exec_())


