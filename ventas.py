from PyQt5 import QtWidgets, QtGui, QtCore
import sqlite3
from ui_utils import bocciolo_logo_widget, get_data_path
from datetime import datetime

db_path = get_data_path('productos.db')

class VentasWindow(QtWidgets.QWidget):
    # señal que indica que las ventas cambiaron (crear/editar/eliminar)
    updated = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ventas - Bocciolo")
        self.setMinimumSize(1000, 700)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(12,12,12,12)
        # Logo y controles
        layout.addWidget(bocciolo_logo_widget(100))
        hl = QtWidgets.QHBoxLayout()
        btn_full = QtWidgets.QPushButton("Pantalla completa"); btn_full.setObjectName("btnFull"); btn_full.clicked.connect(self.showMaximized)
        btn_restore = QtWidgets.QPushButton("Restaurar tamaño"); btn_restore.setObjectName("btnRestore"); btn_restore.clicked.connect(self.showNormal)
        hl.addStretch(); hl.addWidget(btn_full); hl.addWidget(btn_restore); hl.addStretch()
        layout.addLayout(hl)

        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Buscar por producto o cliente...")
        self.search_bar.textChanged.connect(self.filter_ventas)
        layout.addWidget(self.search_bar)

        # Tabla
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels(["ID", "Producto", "Cliente", "Tipo", "Cantidad", "Color", "Costo unit.", "Venta $", "Pago", "Pagado", "Fecha"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Botones
        btns_h = QtWidgets.QHBoxLayout()
        self.btn_new = QtWidgets.QPushButton("Registrar nueva venta")
        self.btn_edit = QtWidgets.QPushButton("Editar venta seleccionada")
        self.btn_delete = QtWidgets.QPushButton("Eliminar venta seleccionada")
        self.btn_new.clicked.connect(self.nueva_venta)
        self.btn_edit.clicked.connect(self.editar_venta)
        self.btn_delete.clicked.connect(self.eliminar_venta)
        btns_h.addWidget(self.btn_new)
        btns_h.addWidget(self.btn_edit)
        btns_h.addWidget(self.btn_delete)
        layout.addLayout(btns_h)

        self.setLayout(layout)
        self.load_ventas()

    def filter_ventas(self, text):
        self.load_ventas(filter_text=text)

    def load_ventas(self, filter_text=None):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        query = '''SELECT v.id, p.nombre, v.cliente, v.tipo, v.cantidad, v.color, v.costo_unitario, v.costo_venta, v.pago, v.pagado, v.fecha 
                 FROM ventas v
                 JOIN productos p ON v.producto_id = p.id'''
        params = []
        if filter_text:
            query += " WHERE p.nombre LIKE ? OR v.cliente LIKE ?"
            term = f"%{filter_text}%"
            params.extend([term, term])
        query += " ORDER BY v.id DESC"

        c.execute(query, params)
        ventas = c.fetchall()
        self.table.setRowCount(0)
        for v in ventas:
            r = self.table.rowCount()
            self.table.insertRow(r)
            # Ajustar los valores a las columnas correctas
            vals = [v[0], v[1], v[2] or "", v[3] or "", v[4], v[5] or "", v[6] or 0, v[7] or 0, v[8] or "", ("Sí" if v[9] else "No"), v[10] or ""]
            for col, val in enumerate(vals):
                itm = QtWidgets.QTableWidgetItem(str(val))
                itm.setTextAlignment(QtCore.Qt.AlignCenter)
                self.table.setItem(r, col, itm)
        conn.close()

    def nueva_venta(self):
        dlg = NuevaVentaDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            producto_id, cliente, tipo, cantidad, color, costo_unit, costo_venta, pago, pagado = dlg.get_data()
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            # Baja stock
            c.execute("UPDATE productos SET cantidad = cantidad - ? WHERE id=?", (cantidad, producto_id))
            # Inserto venta con fecha ahora
            fecha = datetime.now().isoformat(sep=' ')
            c.execute('''INSERT INTO ventas (producto_id, cliente, tipo, cantidad, color, costo_unitario, costo_venta, pago, proveedor, pagado, fecha)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, (SELECT proveedor FROM productos WHERE id=?), ?, ?)''',
                      (producto_id, cliente, tipo, cantidad, color, costo_unit, costo_venta, pago, producto_id, pagado, fecha))
            venta_id = c.lastrowid
            if not pagado:
                c.execute("INSERT INTO fiado (venta_id, cliente, monto, pagado) VALUES (?, ?, ?, 0)", (venta_id, cliente, costo_venta))
            conn.commit()
            conn.close()
            self.load_ventas()
            # emitir señal para actualizar dashboard y otros
            self.updated.emit()

    def editar_venta(self):
        sel = self.table.currentRow()
        if sel < 0:
            QtWidgets.QMessageBox.information(self, "Seleccionar", "Seleccioná una venta para editar.")
            return
        venta_id = int(self.table.item(sel, 0).text())
        dlg = EditVentaDialog(self, venta_id)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            # después de guardar, recargo tabla y aviso con señal
            self.load_ventas()
            self.updated.emit()

    def eliminar_venta(self):
        sel = self.table.currentRow()
        if sel < 0:
            QtWidgets.QMessageBox.information(self, "Seleccionar", "Seleccioná una venta para eliminar.")
            return
        venta_id = int(self.table.item(sel, 0).text())
        confirm = QtWidgets.QMessageBox.question(self, "Confirmar", "Eliminar venta seleccionada? Se restaurará el stock del producto.", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if confirm != QtWidgets.QMessageBox.Yes:
            return
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        # Antes de borrar, recuperar info para restaurar stock y borrar fiado
        c.execute("SELECT producto_id, cantidad FROM ventas WHERE id=?", (venta_id,))
        row = c.fetchone()
        if row:
            producto_id, cantidad = row
            # restaurar stock
            c.execute("UPDATE productos SET cantidad = cantidad + ? WHERE id=?", (cantidad, producto_id))
        # borrar fiado asociado
        c.execute("DELETE FROM fiado WHERE venta_id=?", (venta_id,))
        # borrar venta
        c.execute("DELETE FROM ventas WHERE id=?", (venta_id,))
        conn.commit()
        conn.close()
        self.load_ventas()
        self.updated.emit()


class NuevaVentaDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, initial=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva venta" if not initial else "Editar venta")
        self.resize(480, 420)
        layout = QtWidgets.QFormLayout()

        # Productos disponibles
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT id, nombre, cantidad, costo_unitario, costo_venta FROM productos")
        prods = c.fetchall()
        conn.close()

        self.prod_cb = QtWidgets.QComboBox()
        for p in prods:
            self.prod_cb.addItem(f"{p[1]} (Stock: {p[2]}) - ${p[4]}", p[0])
        self.cliente = QtWidgets.QLineEdit()
        self.tipo = QtWidgets.QLineEdit()
        self.cantidad = QtWidgets.QSpinBox(); self.cantidad.setRange(1, 999)
        self.color = QtWidgets.QLineEdit()
        self.costo_unit = QtWidgets.QSpinBox(); self.costo_unit.setRange(0, 1000000)
        self.costo_venta = QtWidgets.QSpinBox(); self.costo_venta.setRange(0, 1000000)
        self.pago_cb = QtWidgets.QComboBox(); self.pago_cb.addItems(["efectivo", "tarjeta", "transf", "fiado"])
        self.pagado_cb = QtWidgets.QComboBox(); self.pagado_cb.addItems(["Sí", "No"])

        layout.addRow("Producto:", self.prod_cb)
        layout.addRow("Cliente:", self.cliente)
        layout.addRow("Tipo:", self.tipo)
        layout.addRow("Cantidad:", self.cantidad)
        layout.addRow("Color:", self.color)
        layout.addRow("Costo Unit.:", self.costo_unit)
        layout.addRow("Costo Venta:", self.costo_venta)
        layout.addRow("Forma de pago:", self.pago_cb)
        layout.addRow("Pagado:", self.pagado_cb)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        self.setLayout(layout)

        # si hay datos iniciales (edición), cargarlos
        if initial:
            self.load_initial(initial)

    def load_initial(self, venta_id):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT producto_id, cliente, tipo, cantidad, color, costo_unitario, costo_venta, pago, pagado FROM ventas WHERE id=?", (venta_id,))
        row = c.fetchone()
        conn.close()
        if not row:
            return
        producto_id, cliente, tipo, cantidad, color, costo_unit, costo_venta, pago, pagado = row
        # seleccionar producto en combo
        index = self.prod_cb.findData(producto_id)
        if index >= 0:
            self.prod_cb.setCurrentIndex(index)
        self.cliente.setText(cliente or "")
        self.tipo.setText(tipo or "")
        self.cantidad.setValue(cantidad or 1)
        self.color.setText(color or "")
        self.costo_unit.setValue(costo_unit or 0)
        self.costo_venta.setValue(costo_venta or 0)
        p_index = self.pago_cb.findText(pago or "")
        if p_index >= 0:
            self.pago_cb.setCurrentIndex(p_index)
        self.pagado_cb.setCurrentIndex(0 if pagado else 1)  # 0 -> Sí, 1 -> No

    def get_data(self):
        producto_id = self.prod_cb.currentData()
        cliente = self.cliente.text().strip()
        tipo = self.tipo.text().strip()
        cantidad = self.cantidad.value()
        color = self.color.text().strip()
        costo_unit = self.costo_unit.value()
        costo_venta = self.costo_venta.value()
        pago = self.pago_cb.currentText()
        pagado = 1 if self.pagado_cb.currentText() == "Sí" else 0
        return producto_id, cliente, tipo, cantidad, color, costo_unit, costo_venta, pago, pagado


class EditVentaDialog(NuevaVentaDialog):
    def __init__(self, parent=None, venta_id=None):
        super().__init__(parent, initial=None)
        self.setWindowTitle("Editar venta")
        self.venta_id = venta_id
        # Recargar productos
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT id, nombre, cantidad, costo_unitario, costo_venta FROM productos")
        prods = c.fetchall()
        conn.close()
        self.prod_cb.clear()
        for p in prods:
            self.prod_cb.addItem(f"{p[1]} (Stock: {p[2]}) - ${p[4]}", p[0])
        # Cargar datos actuales
        self.load_initial(venta_id)
        # reconectar botón Ok para save_changes
        for b in self.findChildren(QtWidgets.QDialogButtonBox):
            try:
                b.accepted.disconnect()
            except Exception:
                pass
            b.accepted.connect(self.save_changes)

    def save_changes(self):
        new_producto_id, cliente, tipo, new_cantidad, color, costo_unit, costo_venta, pago, pagado = self.get_data()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        # obtener datos anteriores
        c.execute("SELECT producto_id, cantidad, pagado FROM ventas WHERE id=?", (self.venta_id,))
        prev = c.fetchone()
        if not prev:
            QtWidgets.QMessageBox.critical(self, "Error", "No se encontró la venta en la base.")
            conn.close()
            return
        prev_producto_id, prev_cantidad, prev_pagado = prev

        try:
            # Si cambió el producto, restaurar stock en producto anterior
            if prev_producto_id != new_producto_id:
                # devolver cantidad anterior al producto viejo
                c.execute("UPDATE productos SET cantidad = cantidad + ? WHERE id=?", (prev_cantidad, prev_producto_id))
                # quitar cantidad nueva del producto nuevo
                c.execute("UPDATE productos SET cantidad = cantidad - ? WHERE id=?", (new_cantidad, new_producto_id))
            else:
                # mismo producto -> ajustar por diferencia
                diff = new_cantidad - prev_cantidad
                c.execute("UPDATE productos SET cantidad = cantidad - ? WHERE id=?", (diff, new_producto_id))

            # actualizar la venta (incluye fecha modificación ahora)
            fecha = datetime.now().isoformat(sep=' ')
            c.execute('''UPDATE ventas SET producto_id=?, cliente=?, tipo=?, cantidad=?, color=?, costo_unitario=?, costo_venta=?, pago=?, pagado=?, proveedor=(SELECT proveedor FROM productos WHERE id=?), fecha=?
                         WHERE id=?''',
                      (new_producto_id, cliente, tipo, new_cantidad, color, costo_unit, costo_venta, pago, pagado, new_producto_id, fecha, self.venta_id))

            # actualizar fiado según nuevo estado pagado
            c.execute("SELECT id FROM fiado WHERE venta_id=?", (self.venta_id,))
            fiado_row = c.fetchone()
            if pagado == 0:
                if fiado_row:
                    c.execute("UPDATE fiado SET cliente=?, monto=?, pagado=0 WHERE venta_id=?", (cliente, costo_venta, self.venta_id))
                else:
                    c.execute("INSERT INTO fiado (venta_id, cliente, monto, pagado) VALUES (?, ?, ?, 0)", (self.venta_id, cliente, costo_venta))
            else:
                if fiado_row:
                    c.execute("UPDATE fiado SET pagado=1 WHERE venta_id=?", (self.venta_id,))

            conn.commit()
            QtWidgets.QMessageBox.information(self, "Guardado", "Venta actualizada correctamente.")
            self.accept()
        except Exception as e:
            conn.rollback()
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al guardar cambios: {e}")
        finally:
            conn.close()