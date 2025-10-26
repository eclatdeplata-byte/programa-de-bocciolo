import os
import sys
from PyQt5 import QtWidgets, QtGui, QtCore

def get_asset_path(relative_path):
    """ Obtiene la ruta absoluta al recurso de solo lectura (asset), funciona para desarrollo y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_data_path(relative_path):
    """
    Obtiene la ruta absoluta a un archivo de datos persistente.
    Para el ejecutable, usa la carpeta AppData del usuario.
    Para desarrollo, usa el directorio actual.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # La aplicación está 'congelada' (ejecutable)
        # Usar 'APPDATA' para guardar los datos de la aplicación
        app_data_path = os.path.join(os.environ['APPDATA'], 'Bocciolo Programa')
        
        # Crear el directorio si no existe
        if not os.path.exists(app_data_path):
            os.makedirs(app_data_path)
            
        application_path = app_data_path
    else:
        # La aplicación se está ejecutando desde el código fuente
        application_path = os.path.abspath(".")
    
    return os.path.join(application_path, relative_path)

def bocciolo_logo_widget(size=120):
    """
    Devuelve un QLabel con el logo redimensionado. Si no encuentra logo.png
    devuelve un QLabel vacío (sin romper la app).
    """
    logo = QtWidgets.QLabel()
    logo_path = get_asset_path("logo.png") # Actualizado para usar el nuevo nombre
    pixmap = QtGui.QPixmap(logo_path)
    if not pixmap.isNull():
        logo.setPixmap(pixmap.scaled(size, size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
    else:
        # espacio reservado si no existe la imagen
        logo.setFixedSize(size, size)
    logo.setAlignment(QtCore.Qt.AlignCenter)
    return logo