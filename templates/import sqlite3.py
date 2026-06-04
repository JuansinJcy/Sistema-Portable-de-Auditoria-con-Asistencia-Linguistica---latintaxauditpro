import sqlite3
from flask import Flask, render_template, request, jsonify
import webview
import threading
import sys

app = Flask(__name__)

# 1. Configuración de Base de Datos Local
def init_db():
    conn = sqlite3.connect('latintax_local.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            concepto_ingles TEXT,
            concepto_espanol TEXT,
            monto_base REAL,
            sales_tax REAL,
            total_calculado REAL,
            estado_auditoria TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 2. Diccionario de Asistencia Lingüística (Traducción Contextual Básica)
diccionario_financiero = {
    "invoice": "Factura",
    "receipt": "Recibo",
    "taxes": "Impuestos",
    "fee": "Tarifa/Cargo",
    "shipping": "Envío",
    "supplies": "Suministros"
}

# 3. Rutas del Servidor Local
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/procesar', methods=['POST'])
def procesar_factura():
    datos = request.json
    concepto_ing = datos['concepto'].lower()
    monto_base = float(datos['monto'])
    tax_rate = float(datos['tax_rate']) / 100
    
    # Lógica de Traducción
    concepto_esp = diccionario_financiero.get(concepto_ing, "Concepto No Reconocido (Requiere Revisión)")
    
    # Lógica de Auditoría Matemática
    sales_tax_calculado = monto_base * tax_rate
    total_calculado = monto_base + sales_tax_calculado
    
    # Validación de estado
    estado = "Aprobado" if concepto_esp != "Concepto No Reconocido (Requiere Revisión)" else "Pendiente de Revisión"

    # Persistencia en SQLite
    conn = sqlite3.connect('latintax_local.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO facturas (fecha, concepto_ingles, concepto_espanol, monto_base, sales_tax, total_calculado, estado_auditoria)
        VALUES (date('now'), ?, ?, ?, ?, ?, ?)
    ''', (datos['concepto'], concepto_esp, monto_base, sales_tax_calculado, total_calculado, estado))
    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "traduccion": concepto_esp,
        "total_auditado": round(total_calculado, 2),
        "estado": estado
    })

# 4. Inicialización Portable (PyWebView)
def start_server():
    app.run(host='127.0.0.1', port=5000, debug=False)

if __name__ == '__main__':
    init_db()
    # Se ejecuta el servidor Flask en un hilo secundario
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
    # Se lanza la ventana nativa de escritorio
    webview.create_window('LantiNTax Audit Pro', 'http://127.0.0.1:5000', width=900, height=600)
    webview.start()
    sys.exit()