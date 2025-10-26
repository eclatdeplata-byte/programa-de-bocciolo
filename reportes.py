from PyQt5 import QtWidgets, QtCore
import sqlite3
from ui_utils import bocciolo_logo_widget, get_data_path

db_path = get_data_path('productos.db')

class ReportesWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reportes - Bocciolo")
        self.setMinimumSize(900, 600)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(bocciolo_logo_widget(90))
        hl = QtWidgets.QHBoxLayout()
        btn_full = QtWidgets.QPushButton("Pantalla completa"); btn_full.setObjectName("btnFull"); btn_full.clicked.connect(self.showMaximized)
        btn_restore = QtWidgets.QPushButton("Restaurar tamaño"); btn_restore.setObjectName("btnRestore"); btn_restore.clicked.connect(self.showNormal)
        hl.addStretch(); hl.addWidget(btn_full); hl.addWidget(btn_restore); hl.addStretch()
        layout.addLayout(hl)
        # Sencillo: tabla resumen de ventas totales por proveedor
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Proveedor", "Cantidad ventas", "Total $"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_reportes()

    def load_reportes(self):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT proveedor, COUNT(*), SUM(costo_venta) FROM ventas GROUP BY proveedor")
        rows = c.fetchall()
        self.table.setRowCount(0)
        for r in rows:
            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)
            for col, v in enumerate(r):
                itm = QtWidgets.QTableWidgetItem(str(v))
                itm.setTextAlignment(QtCore.Qt.AlignCenter)
                self.table.setItem(row_pos, col, itm)
        conn.close()