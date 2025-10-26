from PyQt5 import QtWidgets, QtCore
from ui_utils import bocciolo_logo_widget, get_data_path
import sqlite3

db_path = get_data_path('productos.db')

class ConfigWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuración - Bocciolo")
        self.setMinimumSize(800, 500)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(bocciolo_logo_widget(90))
        hl = QtWidgets.QHBoxLayout()
        btn_full = QtWidgets.QPushButton("Pantalla completa"); btn_full.setObjectName("btnFull"); btn_full.clicked.connect(self.showMaximized)
        btn_restore = QtWidgets.QPushButton("Restaurar tamaño"); btn_restore.setObjectName("btnRestore"); btn_restore.clicked.connect(self.showNormal)
        hl.addStretch(); hl.addWidget(btn_full); hl.addWidget(btn_restore); hl.addStretch()
        layout.addLayout(hl)
        # Settings básicos: cambiar contraseña de 'lourdes' (ejemplo)
        form = QtWidgets.QFormLayout()
        self.user = QtWidgets.QLineEdit("lourdes"); self.user.setReadOnly(True)
        self.newpass = QtWidgets.QLineEdit(); self.newpass.setEchoMode(QtWidgets.QLineEdit.Password)
        btn_save = QtWidgets.QPushButton("Guardar contraseña")
        btn_save.clicked.connect(self.cambiar_password)
        form.addRow("Usuario:", self.user)
        form.addRow("Nueva contraseña:", self.newpass)
        form.addRow("", btn_save)
        layout.addLayout(form)
        self.setLayout(layout)

    def cambiar_password(self):
        nueva = self.newpass.text().strip()
        if not nueva:
            QtWidgets.QMessageBox.warning(self, "Error", "Ingresa una contraseña válida")
            return
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("UPDATE usuarios SET contraseña=? WHERE usuario=?", (nueva, "lourdes"))
        conn.commit()
        conn.close()
        QtWidgets.QMessageBox.information(self, "Guardado", "Contraseña actualizada")