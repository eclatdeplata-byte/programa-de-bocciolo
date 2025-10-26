from PyQt5 import QtWidgets, QtCore, QtGui
import sqlite3
from datetime import datetime
from ui_utils import get_data_path

db_path = get_data_path('productos.db')

try:
    import pyqtgraph as pg
    HAVE_PG = True
except ImportError:
    HAVE_PG = False

class DashboardWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard - Bocciolo")
        self.setMinimumSize(1000, 600)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)

        # Header
        hl_top = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Dashboard - Resumen de ventas")
        title.setFont(QtGui.QFont("Arial", 20, QtGui.QFont.Bold))
        hl_top.addWidget(title)
        hl_top.addStretch()
        layout.addLayout(hl_top)

        # Filtro de Fechas
        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.setContentsMargins(0, 10, 0, 10)
        filter_layout.addWidget(QtWidgets.QLabel("Desde:"))
        self.date_start = QtWidgets.QDateEdit(calendarPopup=True)
        self.date_start.setDate(QtCore.QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(self.date_start)
        filter_layout.addSpacing(20)
        filter_layout.addWidget(QtWidgets.QLabel("Hasta:"))
        self.date_end = QtWidgets.QDateEdit(calendarPopup=True)
        self.date_end.setDate(QtCore.QDate.currentDate())
        filter_layout.addWidget(self.date_end)
        self.btn_filter = QtWidgets.QPushButton("Actualizar / Filtrar")
        self.btn_filter.clicked.connect(self.update_dashboard)
        filter_layout.addWidget(self.btn_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Metrics
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(12)
        self.lbl_total_ventas = QtWidgets.QLabel("Total ventas: $0")
        self.lbl_total_costos = QtWidgets.QLabel("Total costos: $0")
        self.lbl_ganancia = QtWidgets.QLabel("Ganancia: $0")
        self.lbl_total_ingresado = QtWidgets.QLabel("Total ingresado (pagado): $0")
        self.lbl_total_pendiente = QtWidgets.QLabel("Pendiente (fiado total): $0")
        self.lbl_efectivo = QtWidgets.QLabel("Efectivo: $0")
        self.lbl_tarjeta = QtWidgets.QLabel("Tarjeta: $0")
        self.lbl_transf = QtWidgets.QLabel("Transferencia: $0")

        labels = [
            self.lbl_total_ventas, self.lbl_total_costos, self.lbl_ganancia, self.lbl_total_ingresado,
            self.lbl_total_pendiente, self.lbl_efectivo, self.lbl_tarjeta, self.lbl_transf
        ]
        for i, lbl in enumerate(labels):
            lbl.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            box = QtWidgets.QFrame()
            box.setFrameShape(QtWidgets.QFrame.StyledPanel)
            v = QtWidgets.QVBoxLayout()
            v.addWidget(lbl)
            box.setLayout(v)
            grid.addWidget(box, i // 4, i % 4)

        layout.addLayout(grid)

        # Graph area
        if HAVE_PG:
            self.plot_widget = pg.PlotWidget(title="Ventas por forma de pago")
            layout.addWidget(self.plot_widget, 2)
        else:
            lbl_no = QtWidgets.QLabel("Instalá 'pyqtgraph' para ver gráficos (pip install pyqtgraph).")
            lbl_no.setStyleSheet("color: gray;")
            layout.addWidget(lbl_no)

        # Ventas en rango
        layout.addSpacing(8)
        self.lbl_recent = QtWidgets.QLabel("Ventas en el rango de fechas seleccionado")
        self.lbl_recent.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Bold))
        layout.addWidget(self.lbl_recent)
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Fecha", "Producto", "Cliente", "Cantidad", "Venta $", "Pago", "Pagado"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch) # Stretch producto
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.update_dashboard()

    def _query_one(self, sql, params=()):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(sql, params)
        r = c.fetchone()
        conn.close()
        return r[0] if r and r[0] is not None else 0

    def update_dashboard(self):
        start_date = self.date_start.date().toString("yyyy-MM-dd 00:00:00")
        end_date = self.date_end.date().toString("yyyy-MM-dd 23:59:59")
        date_range = (start_date, end_date)

        # metrics
        total_ventas = self._query_one("SELECT SUM(costo_venta) FROM ventas WHERE fecha BETWEEN ? AND ?", date_range)
        total_costos = self._query_one("SELECT SUM(costo_unitario) FROM ventas WHERE fecha BETWEEN ? AND ?", date_range)
        total_ingresado = self._query_one("SELECT SUM(costo_venta) FROM ventas WHERE pagado=1 AND fecha BETWEEN ? AND ?", date_range)
        
        # El fiado pendiente no tiene fecha, se muestra el total actual.
        total_pendiente = self._query_one("SELECT SUM(monto) FROM fiado WHERE pagado=0")

        efectivo = self._query_one("SELECT SUM(costo_venta) FROM ventas WHERE pago='efectivo' AND fecha BETWEEN ? AND ?", date_range)
        tarjeta = self._query_one("SELECT SUM(costo_venta) FROM ventas WHERE pago='tarjeta' AND fecha BETWEEN ? AND ?", date_range)
        transf = self._query_one("SELECT SUM(costo_venta) FROM ventas WHERE pago='transf' AND fecha BETWEEN ? AND ?", date_range)

        ganancia = total_ventas - total_costos

        self.lbl_total_ventas.setText(f"Total ventas: ${int(total_ventas):,}")
        self.lbl_total_costos.setText(f"Total costos: ${int(total_costos):,}")
        self.lbl_ganancia.setText(f"Ganancia: ${int(ganancia):,}")
        self.lbl_total_ingresado.setText(f"Ingresado (pagado): ${int(total_ingresado):,}")
        self.lbl_total_pendiente.setText(f"Pendiente (fiado total): ${int(total_pendiente):,}")
        self.lbl_efectivo.setText(f"Efectivo: ${int(efectivo):,}")
        self.lbl_tarjeta.setText(f"Tarjeta: ${int(tarjeta):,}")
        self.lbl_transf.setText(f"Transferencia: ${int(transf):,}")

        # tabla de ventas en el rango
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT id, fecha, producto_id, cliente, cantidad, costo_venta, pago, pagado FROM ventas WHERE fecha BETWEEN ? AND ? ORDER BY fecha DESC", date_range)
        rows = c.fetchall()
        self.table.setRowCount(0)
        for row in rows:
            vid, fecha, pid, cliente, cantidad, venta_val, pago, pagado = row
            
            c2 = conn.cursor()
            c2.execute("SELECT nombre FROM productos WHERE id=?", (pid,))
            prod = c2.fetchone()
            prod_name = prod[0] if prod else "N/A"
            
            r = self.table.rowCount()
            self.table.insertRow(r)
            
            # Formatear fecha para mostrar
            fecha_dt = datetime.strptime(fecha.split(" ")[0], '%Y-%m-%d')
            fecha_str = fecha_dt.strftime('%d/%m/%Y')

            vals = [vid, fecha_str, prod_name, cliente or "", cantidad, f"${venta_val or 0:,}", pago or "", ("Sí" if pagado else "No")]
            for col, v in enumerate(vals):
                it = QtWidgets.QTableWidgetItem(str(v))
                it.setTextAlignment(QtCore.Qt.AlignCenter)
                self.table.setItem(r, col, it)
        conn.close()

        # actualizar gráfico
        if HAVE_PG:
            self.plot_widget.clear()
            labels = ['efectivo', 'tarjeta', 'transf']
            values = [efectivo, tarjeta, transf]
            x = list(range(len(labels)))
            try:
                bg = pg.BarGraphItem(x=x, height=values, width=0.6, brush='m')
                self.plot_widget.addItem(bg)
                ax = self.plot_widget.getAxis('bottom')
                ax.setTicks([list(zip(x, labels))])
            except Exception as e:
                print(f"Error al crear el gráfico: {e}")