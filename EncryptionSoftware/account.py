import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileSystemModel, QTableView, QMessageBox
from PyQt5.QtCore import QDir
from encryptmode import ECB, OFB, CBC, CFB, EncryptMode, LUC
import sys
import requests
from variables import SERVER_ADDRESS
import json
import random
import string


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


class Account(QMainWindow):
    def __init__(self, login: str = '', user_id: str = '1', parent=None):
        super(Account, self).__init__(parent)
        self.encryption_type = None
        self.chosen_file = None
        self.chosen_serv_file = None
        self.user_id = user_id
        self.login = login
        self.key = None
        self.key_crypt = ''
        self.c_0 = None
        self.generate_keys()

        self.user_dir = f'file_to_send/{self.user_id}/'
        self.file_model = QFileSystemModel(self)
        self.serv_files_model = QStandardItemModel(self)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.menubar = QtWidgets.QMenuBar(self)

        self.centralwidget = QtWidgets.QWidget(self)
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget1 = QtWidgets.QWidget(self.centralwidget)

        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_2 = QtWidgets.QGridLayout(self.widget1)

        self.pb_refresh = QtWidgets.QPushButton(self.widget1)
        self.pb_send = QtWidgets.QPushButton(self.widget1)
        self.pb_download = QtWidgets.QPushButton(self.widget1)
        self.pb_decrypt = QtWidgets.QPushButton(self.widget1)
        self.progressBar = QtWidgets.QProgressBar(self.widget1)

        self.rb_rdh = QtWidgets.QRadioButton(self.widget)
        self.rb_rd = QtWidgets.QRadioButton(self.widget)
        self.rb_ctr = QtWidgets.QRadioButton(self.widget)
        self.rb_ofb = QtWidgets.QRadioButton(self.widget)
        self.rb_cfb = QtWidgets.QRadioButton(self.widget)
        self.rb_cbc = QtWidgets.QRadioButton(self.widget)
        self.rb_ecb = QtWidgets.QRadioButton(self.widget)
        self.enc_mode = None
        self.encrypter = None

        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)

        self.lv_files_server = QtWidgets.QListView(self.centralwidget)
        self.lv_files = QtWidgets.QListView(self.centralwidget)

        self.lb_login = QtWidgets.QLabel(self.centralwidget)
        self.lb_login.setText(login)
        self.label = QtWidgets.QLabel(self.centralwidget)

        self.setup_ui()
        self.add_functions()
        self.add_directories()

    def setup_ui(self):
        self.setObjectName("MainWindow")
        self.resize(700, 373)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.lv_files.setGeometry(QtCore.QRect(180, 40, 230, 210))
        self.lv_files.setObjectName("lv_files")
        self.label.setGeometry(QtCore.QRect(10, 0, 71, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.lb_login.setGeometry(QtCore.QRect(10, 30, 81, 51))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setItalic(True)
        self.lb_login.setFont(font)
        self.lb_login.setObjectName("lb_login")
        self.lv_files_server.setGeometry(QtCore.QRect(450, 40, 230, 210))
        self.lv_files_server.setObjectName("lv_files_server")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(10, 290, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(90, 290, 75, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.label_2.setGeometry(QtCore.QRect(470, 10, 111, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")

        self.label_3.setGeometry(QtCore.QRect(180, 10, 161, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.widget.setGeometry(QtCore.QRect(11, 81, 121, 191))
        self.widget.setObjectName("widget")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.rb_ecb.setEnabled(True)
        self.rb_ecb.setChecked(True)
        self.rb_ecb.setObjectName("rb_ecb")
        self.gridLayout.addWidget(self.rb_ecb, 0, 0, 1, 1)
        self.rb_cbc.setObjectName("rb_cbc")
        self.gridLayout.addWidget(self.rb_cbc, 1, 0, 1, 1)
        self.rb_cfb.setObjectName("rb_cfb")
        self.gridLayout.addWidget(self.rb_cfb, 2, 0, 1, 1)
        self.rb_ofb.setObjectName("rb_ofb")
        self.gridLayout.addWidget(self.rb_ofb, 3, 0, 1, 1)
        self.rb_ctr.setObjectName("rb_ctr")
        self.gridLayout.addWidget(self.rb_ctr, 4, 0, 1, 1)
        self.rb_rd.setObjectName("rb_rd")
        self.gridLayout.addWidget(self.rb_rd, 5, 0, 1, 1)
        self.rb_rdh.setObjectName("rb_rdh")
        self.gridLayout.addWidget(self.rb_rdh, 6, 0, 1, 1)
        self.widget1.setGeometry(QtCore.QRect(180, 260, 491, 56))
        self.widget1.setObjectName("widget1")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        font = QtGui.QFont()
        font.setPointSize(10)
        self.progressBar.setFont(font)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout_2.addWidget(self.progressBar, 0, 0, 2, 1)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.pb_decrypt.setFont(font)
        self.pb_decrypt.setObjectName("pb_decrypt")
        self.gridLayout_2.addWidget(self.pb_decrypt, 0, 1, 1, 1)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.pb_download.setFont(font)
        self.pb_download.setObjectName("pb_download")
        self.gridLayout_2.addWidget(self.pb_download, 0, 2, 1, 1)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.pb_send.setFont(font)
        self.pb_send.setObjectName("pb_encrypt")
        self.gridLayout_2.addWidget(self.pb_send, 1, 1, 1, 1)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.pb_refresh.setFont(font)
        self.pb_refresh.setObjectName("pb_refresh")
        self.gridLayout_2.addWidget(self.pb_refresh, 1, 2, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 700, 21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.translate_ui()
        QtCore.QMetaObject.connectSlotsByName(self)

    def translate_ui(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "ES"))
        self.label.setText(_translate("MainWindow", "Person:"))
        # self.lb_login.setText(_translate("MainWindow", "Leo"))
        self.label_2.setText(_translate("MainWindow", "Server files"))
        self.label_3.setText(_translate("MainWindow", "Directory files"))
        self.pushButton.setText(_translate("MainWindow", "Refresh"))
        self.pushButton_2.setText(_translate("MainWindow", "Download"))
        self.rb_ecb.setText(_translate("MainWindow", "ECB"))
        self.rb_cbc.setText(_translate("MainWindow", "CBC"))
        self.rb_cfb.setText(_translate("MainWindow", "CFB"))
        self.rb_ofb.setText(_translate("MainWindow", "OFB"))
        self.rb_ctr.setText(_translate("MainWindow", "CTR"))
        self.rb_rd.setText(_translate("MainWindow", "RD"))
        self.rb_rdh.setText(_translate("MainWindow", "RD+H"))
        self.pb_decrypt.setText(_translate("MainWindow", "Decrypt file"))
        self.pb_download.setText(_translate("MainWindow", "Download"))
        self.pb_send.setText(_translate("MainWindow", "Send to server"))
        self.pb_refresh.setText(_translate("MainWindow", "Refresh"))

    def generate_keys(self):
        self.key = Account.generate_key()
        print(self.key)
        self.c_0 = Account.generate_key()
        print(self.key)
        self.encrypt_symmetric_key()
        try:
            resp = requests.post(f"{SERVER_ADDRESS}/key/{self.login}?key={self.key}&c_0={self.c_0}")
        except requests.ConnectionError:
            message = QMessageBox()
            message.setWindowTitle("Error connection")
            message.setText("Can not connect to server")
            message.setIcon(QMessageBox.Warning)
            message.exec_()

    def encrypt_symmetric_key(self):
        try:
            resp = requests.get(f"{SERVER_ADDRESS}/key_asymmetric/{self.login}")
            print(resp.json())

            for ent in self.key:
                # print(LUC.encrypt_num(ord(ent), resp.json()['e'], resp.json()['n']))
                self.key_crypt += f"{LUC.encrypt_num(ord(ent), resp.json()['e'], resp.json()['n'])}"
            print(self.key_crypt)

        except requests.ConnectionError:
            message = QMessageBox()
            message.setWindowTitle("Error connection")
            message.setText("Can not connect to server")
            message.setIcon(QMessageBox.Warning)
            message.exec_()

    def add_functions(self):
        self.pb_refresh.clicked.connect(self.refresh_tables)
        self.pb_decrypt.clicked.connect(self.decrypt)
        self.pb_send.clicked.connect(self.send_to_server)
        self.pb_download.clicked.connect(self.download)
        self.lv_files.doubleClicked[QtCore.QModelIndex].connect(self.double_clicked_table)
        self.lv_files.clicked[QtCore.QModelIndex].connect(self.clicked_table)
        self.lv_files_server.clicked[QtCore.QModelIndex].connect(self.clicked_serv_files)

    def add_directories(self):
        self.file_model.setFilter(QDir.AllEntries)
        self.file_model.setRootPath("C:/Users/leo/PycharmProjects/EncryptionSoftware")
        self.lv_files.setModel(self.file_model)
        self.lv_files.setRootIndex(
            self.file_model.index(f"C:/Users/leo/PycharmProjects/EncryptionSoftware/file_to_send/{self.user_id}"))
        try:
            resp = requests.get(f"{SERVER_ADDRESS}/filenames/{self.user_id}")
            print(json.dumps(resp.json()))
            for ent in resp.json():
                item = QStandardItem(ent['name'])
                self.serv_files_model.appendRow(item)
            self.lv_files_server.setModel(self.serv_files_model)
        except requests.ConnectionError:
            message = QMessageBox()
            message.setWindowTitle("Error connection")
            message.setText("Can not connect to server")
            message.setIcon(QMessageBox.Warning)
            message.exec_()

    def double_clicked_table(self, index):
        item = self.file_model.fileInfo(index)
        if item.fileName() == "..":
            directory = item.dir()
            directory.cdUp()
            self.lv_files.setRootIndex(self.file_model.index(directory.absolutePath()))
        elif item.fileName() == ".":
            self.lv_files.setRootIndex(self.file_model.index(""))
        elif item.isDir():
            self.lv_files.setRootIndex(index)

    def clicked_serv_files(self, index):
        self.chosen_serv_file = self.lv_files_server.currentIndex().data()
        print(self.chosen_serv_file)

    def clicked_table(self, index):
        self.chosen_file = self.lv_files.currentIndex().data()
        print(self.chosen_file)

    @staticmethod
    def generate_key():
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(16))

    def refresh_tables(self):
        try:
            resp = requests.get(f"{SERVER_ADDRESS}/filenames/{self.user_id}")
            self.serv_files_model.clear()
            print(json.dumps(resp.json()))
            for ent in resp.json():
                item = QStandardItem(ent['name'])
                self.serv_files_model.appendRow(item)
        except requests.ConnectionError:
            message = QMessageBox()
            message.setWindowTitle("Error connection")
            message.setText("Can not connect to server")
            message.setIcon(QMessageBox.Warning)
            message.exec_()

    def decrypt(self):
        pass
        # TODO: Расшифровка файла

    def rb_checked(self):
        if self.rb_rdh.isChecked():
            self.encrypter = ECB(self.key.encode())
            self.encryption_type = 'ECB'
        elif self.rb_rd.isChecked():
            self.encrypter = ECB(self.key.encode())
            self.encryption_type = 'ECB'
        elif self.rb_ecb.isChecked():
            self.encrypter = ECB(self.key.encode())
            self.encryption_type = 'ECB'
        elif self.rb_cbc.isChecked():
            self.encrypter = CBC(self.key.encode(), self.c_0.encode())
            self.encryption_type = 'CBC'
        elif self.rb_cfb.isChecked():
            self.encrypter = CFB(self.key.encode(), self.c_0.encode())
            self.encryption_type = 'CFB'
        elif self.rb_ctr.isChecked():
            self.encrypter = ECB(self.key.encode())
            self.encryption_type = 'ECB'
        elif self.rb_ofb.isChecked():
            self.encrypter = OFB(self.key.encode(), self.c_0.encode())
            self.encryption_type = 'OFB'

    def send_to_server(self):
        self.rb_checked()
        if not self.chosen_file:
            message = QMessageBox()
            message.setWindowTitle("Error file click")
            message.setText("Choose the file!")
            message.setIcon(QMessageBox.Warning)
            message.exec_()
        else:
            if os.path.exists(self.user_dir + self.chosen_file):
                try:
                    with open(self.user_dir + self.chosen_file, 'rb') as f:
                        open_text = f.read()

                    enc = self.encrypter.encode(open_text)
                    with open(f"temp/{self.chosen_file}", 'wb') as f:
                        f.write(enc)
                    resp = requests.post(f"{SERVER_ADDRESS}/file/upload/{self.user_id}?cypher_type={self.encryption_type}",
                                         files={'file': open(f"temp/{self.chosen_file}", 'rb')})
                    os.remove(f"temp/{self.chosen_file}")
                except requests.ConnectionError:
                    message = QMessageBox()
                    message.setWindowTitle("Error connection")
                    message.setText("Can not connect to server")
                    message.setIcon(QMessageBox.Warning)
                    message.exec_()

            else:
                message = QMessageBox()
                message.setWindowTitle("Error file")
                message.setText("File is not exists")
                message.setIcon(QMessageBox.Warning)
                message.exec_()
        self.chosen_file = None
        self.refresh_tables()

    def download(self):
        if not self.chosen_serv_file:
            message = QMessageBox()
            message.setWindowTitle("Error file click")
            message.setText("Choose the file!")
            message.setIcon(QMessageBox.Warning)
            message.exec_()
        else:
            try:
                resp = requests.get(f"{SERVER_ADDRESS}/file/download/{self.user_id}?file_name={self.chosen_serv_file}")
                if resp.status_code == 200 or resp.status_code == 201:
                    if not os.path.exists(f'{self.user_dir}'):
                        os.makedirs(f'{self.user_dir}')
                    with open(self.user_dir + self.chosen_serv_file, 'wb') as f:
                        f.write(resp.content)
                else:
                    message = QMessageBox()
                    message.setWindowTitle("Error file")
                    message.setText("File does not exist on server!")
                    message.setIcon(QMessageBox.Warning)
                    message.exec_()
            except requests.ConnectionError:
                message = QMessageBox()
                message.setWindowTitle("Error connection")
                message.setText("Can not connect to server")
                message.setIcon(QMessageBox.Warning)
                message.exec_()

        self.chosen_serv_file = None
        self.refresh_tables()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Account()
    window.show()
    sys.exit(app.exec_())
