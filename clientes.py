from PyQt5 import QtWidgets, QtCore
import sqlite3
from ui_utils import bocciolo_logo_widget, get_data_path

db_path = get_data_path('productos.db')

class ClientesWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clientes - Bocciolo")
        self.setMinimumSize(900, 650)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(bocciolo_logo_widget(90))
        hl = QtWidgets.QHBoxLayout()
        btn_full = QtWidgets.QPushButton("Pantalla completa"); btn_full.setObjectName("btnFull"); btn_full.clicked.connect(self.showMaximized)
        btn_restore = QtWidgets.QPushButton("Restaurar tamaño"); btn_restore.setObjectName("btnRestore"); btn_restore.clicked.connect(self.showNormal)
        hl.addStretch(); hl.addWidget(btn_full); hl.addWidget(btn_restore); hl.addStretch()
        layout.addLayout(hl)
        # Selector de clienta
        self.cb = QtWidgets.QComboBox()
        self.cb.setEditable(True) # Habilitar búsqueda
        self.cb.currentIndexChanged.connect(self.load_cliente)
        layout.addWidget(self.cb)
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID Venta", "Producto", "Tipo", "Cantidad", "Color", "Venta $", "Pagado", "Proveedor"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_clientes()

    def load_clientes(self):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT DISTINCT cliente FROM ventas WHERE cliente IS NOT NULL AND cliente <> ''")
        rows = c.fetchall()
        self.cb.clear()
        for r in rows:
            self.cb.addItem(r[0])
        conn.close()
        if self.cb.count():
            self.load_cliente()

    def load_cliente(self):
        cliente = self.cb.currentText()
        if not cliente:
            return
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('SELECT id, producto_id, tipo, cantidad, color, costo_venta, pagado, proveedor FROM ventas WHERE cliente=? ORDER BY id DESC', (cliente,))
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
            vals = [row[0], prod_name, row[2], row[3], row[4], row[5], ("Sí" if row[6] else "No"), row[7]]
            for col, v in enumerate(vals):
                itm = QtWidgets.QTableWidgetItem(str(v))
                itm.setTextAlignment(QtCore.Qt.AlignCenter)
                self.table.setItem(r, col, itm)
        conn.close()