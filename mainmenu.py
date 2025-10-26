from PyQt5 import QtWidgets, QtGui, QtCore
from ui_utils import bocciolo_logo_widget
from productos import ProductosWindow
from ventas import VentasWindow
from clientes import ClientesWindow
from operaciones import OperacionesWindow
from proveedores import ProveedoresWindow
from fiado import FiadoWindow
from reportes import ReportesWindow
from configuracion import ConfigWindow
from dashboard import DashboardWindow

class MainMenu(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menú principal - Bocciolo")
        self.setMinimumSize(1200, 800)

        # Diccionario para mantener referencias a ventanas abiertas
        self._wins = {}

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        # Logo y controles
        layout.addWidget(bocciolo_logo_widget(550))
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

        # Título
        label = QtWidgets.QLabel("Menú principal")
        label.setFont(QtGui.QFont("Arial", 36, QtGui.QFont.Bold))
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet("color: #6A1B9A; margin-top: 16px;")
        layout.addWidget(label)

        # Grid de botones
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(12)
        btns = [
            ("Dashboard", lambda: self.open_window("dashboard", DashboardWindow, "Dashboard - Bocciolo")),
            ("Productos", lambda: self.open_window("productos", ProductosWindow, "Productos - Bocciolo")),
            ("Ventas", lambda: self.open_window("ventas", VentasWindow, "Ventas - Bocciolo")),
            ("Clientes", lambda: self.open_window("clientes", ClientesWindow, "Clientes - Bocciolo")),
            ("Operaciones", lambda: self.open_window("operaciones", OperacionesWindow, "Operaciones globales - Bocciolo")),
            ("Proveedores", lambda: self.open_window("proveedores", ProveedoresWindow, "Proveedores - Bocciolo")),
            ("Fiado", lambda: self.open_window("fiado", FiadoWindow, "Fiado - Bocciolo")),
            ("Reportes", lambda: self.open_window("reportes", ReportesWindow, "Reportes - Bocciolo")),
            ("Configuración", lambda: self.open_window("config", ConfigWindow, "Configuración - Bocciolo")),
        ]
        for i, (txt, handler) in enumerate(btns):
            b = QtWidgets.QPushButton(txt)
            b.setMinimumHeight(60)
            b.setStyleSheet("font-size: 18px;")
            b.clicked.connect(handler)
            grid.addWidget(b, i // 3, i % 3)
        layout.addLayout(grid)

        self.setLayout(layout)

    def open_window(self, key, cls, title=None):
        win = self._wins.get(key)
        if win is not None:
            try:
                win.showNormal()
                win.raise_()
                win.activateWindow()
                return
            except Exception:
                self._wins[key] = None

        try:
            win = cls()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo abrir la ventana: {e}")
            import traceback
            traceback.print_exc()
            return

        if title:
            win.setWindowTitle(title)
        win.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        win.destroyed.connect(lambda obj=None, k=key: self._wins.__setitem__(k, None))
        self._wins[key] = win

        # Si abrimos ventas y el dashboard ya existe, conectamos la señal
        if key == "ventas" and self._wins.get("dashboard"):
            try:
                win.updated.connect(self._wins["dashboard"].load_stats)
            except Exception:
                pass
        # Si abrimos dashboard y ventas ya existe, conectamos la señal
        if key == "dashboard" and self._wins.get("ventas"):
            try:
                self._wins["ventas"].updated.connect(win.load_stats)
            except Exception:
                pass

        win.showMaximized()