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

@app.route('/', methods=['GET', 'POST'])
def index():
    mensaje = ''

    try:
        conn = psycopg2.connect(
            dbname='tienda',
            user='postgres',
            password='familiamelgar',
            host='localhost',
            port='5432',    
            options='-c client_encoding=UTF8'
        )
        cur = conn.cursor()

        if request.method == 'POST':
            tipo = request.form['tipo']
            talla = request.form['talla']
            genero = request.form['genero']
            marca = request.form['marca']

            try:
                cur.execute(
                    "INSERT INTO ropa (tipo, talla, genero, marca) VALUES (%s, %s, %s, %s)",
                    (tipo, talla, genero, marca)
                )
                conn.commit()
                mensaje = '✅ Prenda guardada correctamente.'
            except Exception:
                mensaje = '❌ Error al guardar la prenda.'

        cur.execute("SELECT * FROM ropa ORDER BY id_ropa")
        prendas = cur.fetchall()

        cur.close()
        conn.close()

    except Exception:
        mensaje = '❌ Error de conexión a la base de datos.'
        prendas = []

    return render_template_string(formulario_html, mensaje=mensaje, prendas=prendas)

# 👉 Ruta para procesar la venta
@app.route('/vender', methods=['POST'])
def vender():
    id_ropa = request.form['id_ropa']
    precio_venta = request.form['precio_venta']

    try:
        conn = psycopg2.connect(
            dbname='tienda',
            user='postgres',
            password='familiamelgar',
            host='localhost',
            port='5432',
            options='-c client_encoding=UTF8'
        )
        cur = conn.cursor()

        # Insertar en factura
        cur.execute(
            "INSERT INTO factura (id_ropa, precio_venta) VALUES (%s, %s)",
            (id_ropa, precio_venta)
        )

        # Marcar como vendida
        cur.execute(
            "UPDATE ropa SET estado = 'vendida' WHERE id_ropa = %s",
            (id_ropa,)
        )

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f'❌ Error al vender: {e}')

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
