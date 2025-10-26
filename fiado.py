from PyQt5 import QtWidgets, QtCore
import sqlite3
from ui_utils import bocciolo_logo_widget, get_data_path

db_path = get_data_path('productos.db')

class FiadoWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fiado - Bocciolo")
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
        self.search_bar.setPlaceholderText("Buscar por cliente...")
        self.search_bar.textChanged.connect(self.filter_fiados)
        layout.addWidget(self.search_bar)

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID Fiado", "Venta ID", "Cliente", "Monto", "Pagado"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.table)
        # Botones
        btns = QtWidgets.QHBoxLayout()
        self.btn_mark = QtWidgets.QPushButton("Marcar como pagado")
        self.btn_mark.clicked.connect(self.marcar_pagado)
        btns.addWidget(self.btn_mark)
        layout.addLayout(btns)
        self.setLayout(layout)
        self.load_fiados()

    def filter_fiados(self, text):
        self.load_fiados(filter_text=text)

    def load_fiados(self, filter_text=None):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        query = "SELECT id, venta_id, cliente, monto, pagado FROM fiado ORDER BY id DESC"
        params = []
        if filter_text:
            query = "SELECT id, venta_id, cliente, monto, pagado FROM fiado WHERE cliente LIKE ? ORDER BY id DESC"
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

    def marcar_pagado(self):
        sel = self.table.currentRow()
        if sel < 0:
            return
        fiado_id = int(self.table.item(sel, 0).text())
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("UPDATE fiado SET pagado=1 WHERE id=?", (fiado_id,))
        conn.commit()
        conn.close()
        self.load_fiados()