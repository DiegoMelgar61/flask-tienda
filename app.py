import os
from flask import Flask, request, redirect, render_template_string
import psycopg2

app = Flask(__name__)

formulario_html = '''
    <h2>Registro de Prenda</h2>
    <form method="POST">
        Tipo: <input type="text" name="tipo"><br>
        Talla: <input type="text" name="talla"><br>
        Genero: <input type="text" name="genero"><br>
        Marca: <input type="text" name="marca"><br>
        <input type="submit" value="Guardar">
    </form>
    <p>{{ mensaje }}</p>

    <h3>Prendas registradas:</h3>
    <table border="1" cellpadding="5">
        <tr>
            <th>ID</th>
            <th>Tipo</th>
            <th>Talla</th>
            <th>Genero</th>
            <th>Marca</th>
            <th>Estado</th>
            <th>Acción</th>
        </tr>
        {% for r in prendas %}
        <tr>
            <td>{{ r[0] }}</td>
            <td>{{ r[1] }}</td>
            <td>{{ r[2] }}</td>
            <td>{{ r[3] }}</td>
            <td>{{ r[4] }}</td>
            <td>{{ r[5] }}</td>
            <td>
                {% if r[5] == 'disponible' %}
                    <form method="POST" action="/vender">
                        <input type="hidden" name="id_ropa" value="{{ r[0] }}">
                        Precio Venta: <input type="number" name="precio_venta" step="0.01" required>
                        <input type="submit" value="Vender">
                    </form>
                {% else %}
                    Vendida
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </table>
'''

def conectar_db():
    try:
        DATABASE_URL = os.environ.get("DATABASE_URL")
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print("❌ Error de conexión:", e)
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    mensaje = ''
    prendas = []

    conn = conectar_db()
    if conn:
        try:
            cur = conn.cursor()

            if request.method == 'POST':
                tipo = request.form['tipo']
                talla = request.form['talla']
                genero = request.form['genero']
                marca = request.form['marca']
                try:
                    cur.execute(
                        "INSERT INTO ropa (tipo, talla, genero, marca, estado) VALUES (%s, %s, %s, %s, %s)",
                        (tipo, talla, genero, marca, 'disponible')
                    )
                    conn.commit()
                    mensaje = '✅ Prenda guardada correctamente.'
                except Exception as insert_err:
                    conn.rollback()
                    mensaje = '❌ Error al guardar la prenda.'
                    print("Insert error:", insert_err)

            try:
                cur.execute("SELECT * FROM ropa ORDER BY id_ropa")
                prendas = cur.fetchall()
            except Exception as select_err:
                mensaje = '❌ Error al cargar prendas.'
                print("Select error:", select_err)

            cur.close()
        finally:
            conn.close()
    else:
        mensaje = '❌ Error de conexión a la base de datos.'

    return render_template_string(formulario_html, mensaje=mensaje, prendas=prendas)

@app.route('/vender', methods=['POST'])
def vender():
    id_ropa = request.form['id_ropa']
    precio_venta = request.form['precio_venta']

    conn = conectar_db()
    if conn:
        try:
            cur = conn.cursor()
            try:
                cur.execute(
                    "INSERT INTO factura (id_ropa, precio_venta) VALUES (%s, %s)",
                    (id_ropa, precio_venta)
                )
                cur.execute(
                    "UPDATE ropa SET estado = 'vendida' WHERE id_ropa = %s",
                    (id_ropa,)
                )
                conn.commit()
            except Exception as e:
                conn.rollback()
                print("❌ Error al registrar venta:", e)
            finally:
                cur.close()
        finally:
            conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
