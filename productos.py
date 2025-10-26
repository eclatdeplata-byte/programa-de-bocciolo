from PyQt5 import QtWidgets, QtGui, QtCore
import sqlite3
from ui_utils import bocciolo_logo_widget, get_data_path

db_path = get_data_path('productos.db')

class ProductosWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Productos - Bocciolo")
        self.setMinimumSize(1000, 700)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(12,12,12,12)
        # Logo y controles
        layout.addWidget(bocciolo_logo_widget(100))
        hl = QtWidgets.QHBoxLayout()
        btn_full = QtWidgets.QPushButton("Pantalla completa")
        btn_full.setObjectName("btnFull")
        btn_full.clicked.connect(self.showMaximized)
        btn_restore = QtWidgets.QPushButton("Restaurar tamaño")
        btn_restore.setObjectName("btnRestore")
        btn_restore.clicked.connect(self.showNormal)
        hl.addStretch()
        hl.addWidget(btn_full)
        hl.addWidget(btn_restore)
        hl.addStretch()
        layout.addLayout(hl)
        # Tabla
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Cantidad", "Color", "Talle", "Costo unit.", "Costo venta", "Proveedor", "Imagen"])
        
        # Estrategia de ajuste de columnas mejorada
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch) # Nombre
        header.setSectionResizeMode(7, QtWidgets.QHeaderView.Stretch) # Proveedor
        for col in [0, 2, 3, 4, 5, 6, 8]:
            header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)

        # Buscador
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Buscar por nombre, color, proveedor...")
        self.search_bar.textChanged.connect(self.filter_productos)
        layout.addWidget(self.search_bar)

        layout.addWidget(self.table)
        # Botones
        btns_layout = QtWidgets.QHBoxLayout()
        self.btn_add = QtWidgets.QPushButton("Agregar producto")
        self.btn_edit = QtWidgets.QPushButton("Editar seleccionado")
        self.btn_del = QtWidgets.QPushButton("Eliminar seleccionado")
        self.btn_add.clicked.connect(self.add_producto)
        self.btn_edit.clicked.connect(self.edit_producto)
        self.btn_del.clicked.connect(self.delete_producto)
        btns_layout.addWidget(self.btn_add)
        btns_layout.addWidget(self.btn_edit)
        btns_layout.addWidget(self.btn_del)
        layout.addLayout(btns_layout)
        self.setLayout(layout)
        self.load_productos()

    def filter_productos(self, text):
        self.load_productos(filter_text=text)

    def load_productos(self, filter_text=None):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        query = "SELECT id, nombre, cantidad, color, talle, costo_unitario, costo_venta, proveedor, imagen FROM productos"
        params = []
        if filter_text:
            query += " WHERE nombre LIKE ? OR color LIKE ? OR proveedor LIKE ?"
            term = f"%{filter_text}%"
            params = [term, term, term]
        
        c.execute(query, params)
        rows = c.fetchall()
        self.table.setRowCount(0)
        for row in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            for col, val in enumerate(row):
                if col == 8 and val:
                    btn = QtWidgets.QPushButton("Ver")
                    self.table.setCellWidget(r, col, btn)
                    btn.clicked.connect(lambda checked, p=val: self.show_image(p))
                else:
                    item = QtWidgets.QTableWidgetItem(str(val))
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.table.setItem(r, col, item)
        conn.close()

    def show_image(self, path):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Imagen")
        dlg.setMinimumSize(420, 420)

        v = QtWidgets.QVBoxLayout()
        lbl = QtWidgets.QLabel()
        pix = QtGui.QPixmap(path)
        
        if not pix.isNull():
            lbl.setPixmap(pix.scaled(400, 400, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            lbl.setText(f"No se pudo cargar la imagen.\nVerifique que la ruta es correcta y el archivo existe.")
        
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        v.addWidget(lbl)
        dlg.setLayout(v)
        dlg.exec_()

    def add_producto(self):
        dlg = ProductoDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            data = dlg.get_data()
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute('''INSERT INTO productos (nombre, cantidad, color, talle, costo_unitario, costo_venta, proveedor, imagen) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', data)
            conn.commit()
            conn.close()
            self.load_productos()

    def edit_producto(self):
        sel = self.table.currentRow()
        if sel < 0:
            return
        prod_id = int(self.table.item(sel, 0).text())
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT nombre, cantidad, color, talle, costo_unitario, costo_venta, proveedor, imagen FROM productos WHERE id=?", (prod_id,))
        row = c.fetchone()
        conn.close()
        dlg = ProductoDialog(self, initial=row)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            data = dlg.get_data()
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute('''UPDATE productos SET nombre=?, cantidad=?, color=?, talle=?, costo_unitario=?, costo_venta=?, proveedor=?, imagen=? WHERE id=?''', (*data, prod_id))
            conn.commit()
            conn.close()
            self.load_productos()

    def delete_producto(self):
        sel = self.table.currentRow()
        if sel < 0:
            return
        prod_id = int(self.table.item(sel, 0).text())
        confirm = QtWidgets.QMessageBox.question(self, "Confirmar", "Eliminar producto seleccionado?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if confirm == QtWidgets.QMessageBox.Yes:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("DELETE FROM productos WHERE id=?", (prod_id,))
            conn.commit()
            conn.close()
            self.load_productos()

class ProductoDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, initial=None):
        super().__init__(parent)
        self.setWindowTitle("Producto")
        layout = QtWidgets.QFormLayout()
        self.nombre = QtWidgets.QLineEdit()
        self.cantidad = QtWidgets.QSpinBox(); self.cantidad.setRange(0,9999)
        self.color = QtWidgets.QLineEdit()
        self.talle = QtWidgets.QLineEdit()
        self.costo_unit = QtWidgets.QSpinBox(); self.costo_unit.setRange(0,1000000)
        self.costo_venta = QtWidgets.QSpinBox(); self.costo_venta.setRange(0,1000000)
        self.proveedor = QtWidgets.QLineEdit()
        self.imagen = QtWidgets.QLineEdit()
        btn_pick = QtWidgets.QPushButton("Seleccionar imagen")
        btn_pick.clicked.connect(self.pick_image)
        layout.addRow("Nombre:", self.nombre)
        layout.addRow("Cantidad:", self.cantidad)
        layout.addRow("Color:", self.color)
        layout.addRow("Talle:", self.talle)
        layout.addRow("Costo unit.:", self.costo_unit)
        layout.addRow("Costo venta:", self.costo_venta)
        layout.addRow("Proveedor:", self.proveedor)
        layout.addRow("Imagen path:", self.imagen)
        layout.addRow("", btn_pick)
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        if initial:
            self.nombre.setText(initial[0]); self.cantidad.setValue(initial[1]); self.color.setText(initial[2])
            self.talle.setText(initial[3]); self.costo_unit.setValue(initial[4]); self.costo_venta.setValue(initial[5])
            self.proveedor.setText(initial[6]); self.imagen.setText(initial[7] or "")
        self.setLayout(layout)

    def pick_image(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", "Imágenes (*.png *.jpg *.jpeg)")
        if p:
            self.imagen.setText(p)

    def get_data(self):
        return (self.nombre.text(), self.cantidad.value(), self.color.text(), self.talle.text(),
                self.costo_unit.value(), self.costo_venta.value(), self.proveedor.text(), self.imagen.text())