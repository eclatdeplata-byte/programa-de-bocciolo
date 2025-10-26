from PyQt5 import QtWidgets, QtCore
import sqlite3
from ui_utils import bocciolo_logo_widget, get_data_path

db_path = get_data_path('productos.db')

class OperacionesWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Operaciones globales - Bocciolo")
        self.setMinimumSize(1000, 700)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(bocciolo_logo_widget(90))
        hl = QtWidgets.QHBoxLayout()
        btn_full = QtWidgets.QPushButton("Pantalla completa"); btn_full.setObjectName("btnFull"); btn_full.clicked.connect(self.showMaximized)
        btn_restore = QtWidgets.QPushButton("Restaurar tamaño"); btn_restore.setObjectName("btnRestore"); btn_restore.clicked.connect(self.showNormal)
        hl.addStretch(); hl.addWidget(btn_full); hl.addWidget(btn_restore); hl.addStretch()
        layout.addLayout(hl)
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(["ID", "Producto", "Cliente", "Tipo", "Cantidad", "Color", "Costo unit.", "Venta $", "Pago", "Proveedor"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_ventas()

    def load_ventas(self):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('SELECT id, producto_id, cliente, tipo, cantidad, color, costo_unitario, costo_venta, pago, proveedor FROM ventas ORDER BY id DESC')
        rows = c.fetchall()
        self.table.setRowCount(0)
        for row in rows:
            prod_name = ""
            c2 = conn.cursor()
            c2.execute("SELECT nombre FROM productos WHERE id=?", (row[1],))
            prod = c2.fetchone()
            if prod:
                prod_name = prod[0]
            r = self.table.rowCount()
            self.table.insertRow(r)
            vals = [row[0], prod_name, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]]
            for col, v in enumerate(vals):
                itm = QtWidgets.QTableWidgetItem(str(v))
                itm.setTextAlignment(QtCore.Qt.AlignCenter)
                self.table.setItem(r, col, itm)
        conn.close()