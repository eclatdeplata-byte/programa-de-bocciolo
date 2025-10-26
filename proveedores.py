from PyQt5 import QtWidgets, QtCore
import sqlite3
from ui_utils import bocciolo_logo_widget, get_data_path

db_path = get_data_path('productos.db')

class ProveedoresWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proveedores - Bocciolo")
        self.setMinimumSize(900, 600)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(bocciolo_logo_widget(90))
        hl = QtWidgets.QHBoxLayout()
        btn_full = QtWidgets.QPushButton("Pantalla completa"); btn_full.setObjectName("btnFull"); btn_full.clicked.connect(self.showMaximized)
        btn_restore = QtWidgets.QPushButton("Restaurar tamaño"); btn_restore.setObjectName("btnRestore"); btn_restore.clicked.connect(self.showNormal)
        hl.addStretch(); hl.addWidget(btn_full); hl.addWidget(btn_restore); hl.addStretch()
        layout.addLayout(hl)
        
        # Buscador
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Buscar por nombre de proveedor...")
        self.search_bar.textChanged.connect(self.filter_proveedores)
        layout.addWidget(self.search_bar)

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Proveedor", "Saldo"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_proveedores()

    def filter_proveedores(self, text):
        self.load_proveedores(filter_text=text)

    def load_proveedores(self, filter_text=None):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        query = "SELECT id, nombre, saldo FROM proveedores"
        params = []
        if filter_text:
            query += " WHERE nombre LIKE ?"
            params.append(f"%{filter_text}%")

        c.execute(query, params)
        rows = c.fetchall()
        self.table.setRowCount(0)
        for row in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            for col, v in enumerate(row):
                itm = QtWidgets.QTableWidgetItem(str(v))
                itm.setTextAlignment(QtCore.Qt.AlignCenter)
                self.table.setItem(r, col, itm)
        conn.close()