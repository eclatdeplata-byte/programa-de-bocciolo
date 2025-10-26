from PyQt5 import QtWidgets, QtGui, QtCore
import sqlite3
from ui_utils import get_data_path, bocciolo_logo_widget

db_path = get_data_path('productos.db')

class LoginWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bienvenida a Bocciolo")
        self.setFixedSize(520, 380)
        layout = QtWidgets.QVBoxLayout()
        
        # Logo
        layout.addWidget(bocciolo_logo_widget(180))

        # Título
        title = QtWidgets.QLabel("¡Bienvenida a Bocciolo!")
        title.setFont(QtGui.QFont("Arial", 22, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("color: #6A1B9A; margin-bottom: 8px;")
        layout.addWidget(title)
        # Inputs
        self.user_input = QtWidgets.QLineEdit()
        self.user_input.setPlaceholderText("Usuario")
        self.user_input.setFixedHeight(38)
        layout.addWidget(self.user_input)
        self.pass_input = QtWidgets.QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña")
        self.pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pass_input.setFixedHeight(38)
        layout.addWidget(self.pass_input)
        # Botón
        login_btn = QtWidgets.QPushButton("Entrar")
        login_btn.setStyleSheet("background-color: #D81B60; color: white; font-size: 18px;")
        login_btn.clicked.connect(self.check_login)
        layout.addWidget(login_btn)
        # Error label
        self.error_label = QtWidgets.QLabel("")
        self.error_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.error_label)
        self.setLayout(layout)

    def check_login(self):
        usuario = self.user_input.text().strip()
        contraseña = self.pass_input.text().strip()
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM usuarios WHERE usuario=? AND contraseña=?', (usuario, contraseña))
        result = c.fetchone()
        conn.close()
        if result:
            self.accept() # Devuelve "Aceptado" a main.py
        else:
            self.error_label.setText("Usuario o contraseña incorrectos")
            self.error_label.setStyleSheet("color: red;")