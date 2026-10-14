from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "cambiar-esta-clave-en-desarrollo"
DB_PATH = Path(__file__).with_name("financontrol.db")


def conectar_db():
    """Abre una conexión a SQLite y permite acceder a las columnas por nombre."""
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def inicializar_db():
    """Crea las tablas necesarias y unas categorías iniciales si la base está vacía."""
    with conectar_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS usuario (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                correo TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS categoria (
                id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                descripcion TEXT
            );

            CREATE TABLE IF NOT EXISTS gasto (
                id_gasto INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion TEXT NOT NULL,
                valor REAL NOT NULL CHECK (valor > 0),
                fecha TEXT NOT NULL,
                id_usuario INTEGER NOT NULL,
                id_categoria INTEGER NOT NULL,
                FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
                FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria)
            );
        """)

        usuario = db.execute("SELECT id_usuario FROM usuario LIMIT 1").fetchone()
        if usuario is None:
            db.execute(
                "INSERT INTO usuario (nombre, correo) VALUES (?, ?)",
                ("Usuario de prueba", "usuario@financontrol.local")
            )

        cantidad = db.execute("SELECT COUNT(*) AS total FROM categoria").fetchone()["total"]
        if cantidad == 0:
            db.executemany(
                "INSERT INTO categoria (nombre, descripcion) VALUES (?, ?)",
                [
                    ("Alimentación", "Compras de alimentos y comidas"),
                    ("Transporte", "Pasajes, combustible y transporte"),
                    ("Servicios", "Pagos de servicios y facturas"),
                    ("Estudio", "Gastos relacionados con estudios"),
                    ("Otros", "Gastos que no pertenecen a otra categoría")
                ]
            )

inicializar_db()

def obtener_categorias():
    with conectar_db() as db:
        return db.execute(
            "SELECT id_categoria, nombre FROM categoria ORDER BY nombre"
        ).fetchall()


@app.route("/")
def inicio():
    with conectar_db() as db:
        resumen = db.execute("""
            SELECT COUNT(*) AS cantidad, COALESCE(SUM(valor), 0) AS total
            FROM gasto
        """).fetchone()
        ultimos = db.execute("""
            SELECT g.id_gasto, g.descripcion, g.valor, g.fecha, c.nombre AS categoria
            FROM gasto g
            JOIN categoria c ON c.id_categoria = g.id_categoria
            ORDER BY g.fecha DESC, g.id_gasto DESC
            LIMIT 5
        """).fetchall()
    return render_template("inicio.html", resumen=resumen, ultimos=ultimos)


@app.route("/gastos")
def listar_gastos():
    with conectar_db() as db:
        gastos = db.execute("""
            SELECT g.id_gasto, g.descripcion, g.valor, g.fecha,
                   c.nombre AS categoria
            FROM gasto g
            JOIN categoria c ON c.id_categoria = g.id_categoria
            ORDER BY g.fecha DESC, g.id_gasto DESC
        """).fetchall()
    return render_template("gastos.html", gastos=gastos)


def validar_formulario(form):
    descripcion = form.get("descripcion", "").strip()
    fecha = form.get("fecha", "").strip()
    valor_texto = form.get("valor", "").strip()
    id_categoria = form.get("id_categoria", "").strip()

    if not descripcion or not fecha or not valor_texto or not id_categoria:
        return None, "Todos los campos son obligatorios."

    try:
        valor = float(valor_texto)
    except ValueError:
        return None, "El valor debe ser un número válido."

    if valor <= 0:
        return None, "El valor del gasto debe ser mayor que cero."

    try:
        categoria_id = int(id_categoria)
    except ValueError:
        return None, "Selecciona una categoría válida."

    if categoria_id not in [int(c["id_categoria"]) for c in obtener_categorias()]:
        return None, "La categoría seleccionada no existe."

    return {
        "descripcion": descripcion,
        "valor": valor,
        "fecha": fecha,
        "id_categoria": categoria_id
    }, None


@app.route("/gastos/nuevo", methods=["GET", "POST"])
def crear_gasto():
    categorias = obtener_categorias()
    if request.method == "POST":
        datos, error = validar_formulario(request.form)
        if error:
            flash(error, "error")
            return render_template("formulario_gasto.html", titulo="Registrar gasto",
                                   categorias=categorias, gasto=request.form), 400

        with conectar_db() as db:
            usuario = db.execute("SELECT id_usuario FROM usuario LIMIT 1").fetchone()
            db.execute("""
                INSERT INTO gasto (descripcion, valor, fecha, id_usuario, id_categoria)
                VALUES (?, ?, ?, ?, ?)
            """, (datos["descripcion"], datos["valor"], datos["fecha"],
                  usuario["id_usuario"], datos["id_categoria"]))
        flash("Gasto registrado correctamente.", "exito")
        return redirect(url_for("listar_gastos"))

    return render_template("formulario_gasto.html", titulo="Registrar gasto",
                           categorias=categorias, gasto={})


@app.route("/gastos/<int:id_gasto>/editar", methods=["GET", "POST"])
def editar_gasto(id_gasto):
    categorias = obtener_categorias()
    with conectar_db() as db:
        gasto = db.execute(
            "SELECT * FROM gasto WHERE id_gasto = ?", (id_gasto,)
        ).fetchone()

    if gasto is None:
        flash("El gasto que intentas editar no existe.", "error")
        return redirect(url_for("listar_gastos"))

    if request.method == "POST":
        datos, error = validar_formulario(request.form)
        if error:
            flash(error, "error")
            return render_template("formulario_gasto.html", titulo="Editar gasto",
                                   categorias=categorias, gasto=request.form), 400

        with conectar_db() as db:
            db.execute("""
                UPDATE gasto
                SET descripcion = ?, valor = ?, fecha = ?, id_categoria = ?
                WHERE id_gasto = ?
            """, (datos["descripcion"], datos["valor"], datos["fecha"],
                  datos["id_categoria"], id_gasto))
        flash("Gasto actualizado correctamente.", "exito")
        return redirect(url_for("listar_gastos"))

    return render_template("formulario_gasto.html", titulo="Editar gasto",
                           categorias=categorias, gasto=dict(gasto))


@app.route("/gastos/<int:id_gasto>/eliminar", methods=["POST"])
def eliminar_gasto(id_gasto):
    with conectar_db() as db:
        resultado = db.execute("DELETE FROM gasto WHERE id_gasto = ?", (id_gasto,))
    if resultado.rowcount:
        flash("Gasto eliminado correctamente.", "exito")
    else:
        flash("El gasto no existe o ya fue eliminado.", "error")
    return redirect(url_for("listar_gastos"))


if __name__ == "__main__":
    inicializar_db()
    app.run(debug=True)
