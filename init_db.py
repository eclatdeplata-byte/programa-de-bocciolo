import os
import sqlite3
from ui_utils import get_data_path

db_path = get_data_path('productos.db')

PRODUCTOS = [
    ("Top artemisa", 1, "tostado", "U", 5800, 15800, "FRESH"),
    ("Top carlota", 1, "avena", "U", 4700, 14700, "FRESH"),
    ("Top carlota", 1, "blanco", "U", 4700, 14700, "FRESH"),
    ("Chaleco Capuchino", 1, "negro", "U", 8100, 20000, "FRESH"),
    ("Chaleco Capuchino", 1, "tostado", "U", 8100, 20000, "FRESH"),
    ("Top lara", 1, "negro", "U", 2100, 13000, "FRESH"),
    ("Top lara", 1, "avena", "U", 2100, 13000, "FRESH"),
    ("Top escarlata", 1, "vison claro", "U", 6900, 16900, "FRESH"),
    ("Top miramar", 1, "negro", "U", 6900, 16900, "FRESH"),
    ("Top ailea", 1, "vison claro", "U", 2500, 13000, "FRESH"),
    ("Top ailea", 1, "vison", "U", 2500, 13000, "FRESH"),
    ("Top ailea", 1, "gris", "U", 2500, 13000, "FRESH"),
    ("Pantalon malta oxford", 1, "tostado", "U", 10500, 22000, "RIMS"),
    ("Top ark", 1, "chocolate", "U", 10500, 22000, "RIMS"),
    ("Top ark", 1, "rosa", "U", 10500, 22000, "RIMS"),
    ("Top ark", 1, "blanco", "U", 10500, 22000, "RIMS"),
    ("Musculosa decco", 1, "negro", "M", 4500, 15500, "RIMS"),
    ("Musculosa decco", 1, "vison", "M", 4500, 15500, "RIMS"),
    ("Top frunci", 1, "negro", "U", 10400, 21500, "RIMS"),
    ("Top frunci", 1, "negro", "U", 10400, 21500, "RIMS"),
    ("Vestido Tita", 1, "amarillo", "U", 14400, 24800, "PAZZI"),
    ("Top mixa", 1, "NyB", "U", 3800, 13800, "PAZZI"),
    ("Top mady", 1, "negro", "U", 3800, 15000, "PAZZI"),
    ("Top mady", 1, "chocolate", "U", 3800, 15000, "PAZZI"),
    ("Top mady", 1, "amarillo", "U", 3800, 15000, "PAZZI"),
    ("Top mady", 1, "celeste", "U", 3800, 15000, "PAZZI"),
    ("Musculosa OTTA", 1, "blanco/choc", "U", 4200, 14200, "PAZZI"),
    ("Musculosa OTTA", 1, "blanco/negr", "U", 4200, 14200, "PAZZI"),
    ("Top logui", 1, "negro", "U", 3000, 13500, "PAZZI"),
    ("Top logui", 1, "chocolate", "U", 3000, 13500, "PAZZI"),
    ("Top logui", 1, "verde", "U", 3000, 13500, "PAZZI"),
    ("Body taz", 1, "negro", "U", 5000, 17000, "PAZZI"),
    ("Top Mor", 1, "blanco", "U", 5000, 12000, "PAZZI"),
    ("remera losan", 1, "blanco", "U", 5000, 12000, "PAZZI"),
    ("remera losan", 1, "negro", "U", 5000, 12500, "PAZZI"),
    ("top pipa (espalda desc)", 1, "negro", "U", 4500, 15000, "PAZZI"),
    ("top pipa (espalda desc)", 1, "bordo", "U", 4500, 15000, "PAZZI"),
    ("remera shay (cuello color)", 1, "beige", "U", 4500, 14500, "PAZZI"),
    ("remera shay (cuello color)", 1, "blanco/rosa", "U", 4500, 14500, "PAZZI"),
    ("top corbat", 1, "negro", "U", 5500, 16500, "BLACK"),
    ("top anie", 1, "blanco", "U", 5500, 16800, "BLACK"),
    ("top maza", 1, "bordo", "U", 6000, 16000, "BLACK"),
    ("top melody", 1, "negro", "U", 5000, 15000, "BLACK"),
    ("top zafiro", 1, "negro", "U", 5000, 13000, "BLACK"),
    ("top zafiro", 1, "beige", "U", 5000, 13000, "BLACK"),
    ("top craf", 1, "negro", "U", 5000, 14000, "BLACK"),
    ("top craf", 1, "chocolate", "U", 5000, 14000, "BLACK"),
    ("blusa tifani", 1, "tostado", "U", 7000, 17000, "BLACK"),
]

PROVEEDORES = ["FRESH", "RIMS", "PAZZI", "BLACK"]

VENTAS_INICIALES = [
    (21, "Diego", "vestido tita", 1, "negro", 14400, 20000, "efectivo", "pazzi", 1),
    (45, "Diego", "top naza", 1, "bordo", 6000, 10000, "tarjeta", "black", 1),
    (24, "Rocio", "top mady", 1, "negro", 3800, 15000, "transf", "pazzi", 1),
    (6, "Rocio", "top lara", 1, "negro", 2100, 13000, "transf", "fresh", 0),
    (8, "Rocio", "top escarlata", 1, "vison claro", 3000, 13500, "transf", "fresh", 0),
    (42, "Rocio", "top corbata", 1, "negro", 6000, 16500, "transf", "black", 1),
    (14, "Vicki", "top ark", 1, "marron", 10500, 21500, "efectivo", "rims", 1),
]

def init_db():
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            cantidad INTEGER,
            color TEXT,
            talle TEXT,
            costo_unitario INTEGER,
            costo_venta INTEGER,
            proveedor TEXT,
            imagen TEXT DEFAULT ""
        )''')
        c.execute('''CREATE TABLE proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE,
            saldo INTEGER DEFAULT 0
        )''')
        for p in PROVEEDORES:
            c.execute('INSERT INTO proveedores (nombre) VALUES (?)', (p,))
        c.execute('''CREATE TABLE usuarios (
            usuario TEXT PRIMARY KEY,
            contraseña TEXT
        )''')
        c.execute("INSERT INTO usuarios (usuario, contraseña) VALUES (?, ?)", ('lourdes', 'lourdes1234'))
        c.execute('''CREATE TABLE ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER,
            cliente TEXT,
            tipo TEXT,
            cantidad INTEGER,
            color TEXT,
            costo_unitario INTEGER,
            costo_venta INTEGER,
            pago TEXT,
            proveedor TEXT,
            pagado INTEGER DEFAULT 1,
            fecha TEXT DEFAULT (datetime('now'))
        )''')
        c.execute('''CREATE TABLE fiado (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER,
            cliente TEXT,
            monto INTEGER,
            pagado INTEGER DEFAULT 0
        )''')
        for p in PRODUCTOS:
            c.execute('''INSERT INTO productos (nombre, cantidad, color, talle, costo_unitario, costo_venta, proveedor)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''', p)
        for venta in VENTAS_INICIALES:
            c.execute('''INSERT INTO ventas 
                (producto_id, cliente, tipo, cantidad, color, costo_unitario, costo_venta, pago, proveedor, pagado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', venta)
            c.execute('UPDATE productos SET cantidad = cantidad - ? WHERE id = ?', (venta[3], venta[0]))
            if venta[9] == 0:
                c.execute('INSERT INTO fiado (venta_id, cliente, monto, pagado) VALUES (last_insert_rowid(), ?, ?, 0)', (venta[1], venta[6]))
        conn.commit()
        conn.close()
    else:
        # Si existe DB, asegurarse que la columna 'fecha' existe en tabla ventas
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("PRAGMA table_info(ventas)")
        cols = [r[1] for r in c.fetchall()]
        if 'fecha' not in cols:
            try:
                c.execute("ALTER TABLE ventas ADD COLUMN fecha TEXT")
                c.execute("UPDATE ventas SET fecha = datetime('now') WHERE fecha IS NULL")
                conn.commit()
            except Exception:
                # No fatal: continuamos si falla la alter (por permisos, etc.)
                pass
        conn.close()

init_db()