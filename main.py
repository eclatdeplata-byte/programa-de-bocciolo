import sys
from PyQt5 import QtWidgets
from login import LoginWindow
from init_db import init_db
from ui_utils import get_asset_path # Importar la función centralizada

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # Cargar la hoja de estilos usando la ruta de recurso correcta
    try:
        qss_path = get_asset_path("bocciolo_style.qss")
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Advertencia: No se encontró 'bocciolo_style.qss'. Usando estilo por defecto.")

    # Inicializar DB
    init_db()

    login_win = LoginWindow()
    if login_win.exec_() == QtWidgets.QDialog.Accepted:
        from mainmenu import MainMenu # Corregido: MainMenu en lugar de MainMenuWindow
        main_win = MainMenu()
        main_win.show()
        sys.exit(app.exec_())

if __name__ == '__main__':
    main()