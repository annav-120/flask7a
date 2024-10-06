from flask import Flask, render_template, request, jsonify
import pusher
import mysql.connector
import datetime
import pytz

app = Flask(__name__)

pusher_client = pusher.Pusher(
    app_id='1864237',
    key='fe0a6fda0635d4db01ce',
    secret='e5c4c8f921f883404989',
    cluster='us2',
    ssl=True
)

def get_db_connection():
    con = mysql.connector.connect(
        host="185.232.14.52",
        database="u760464709_tst_sep",
        user="u760464709_tst_sep_usr",
        password="dJ0CIAFF="
    )
    return con

@app.route("/")
def index():
    return render_template("app.html")

@app.route("/alumnos")
def alumnos():
    return render_template("alumnos.html")

@app.route("/alumnos/guardar", methods=["POST"])
def alumnosGuardar():
    matricula = request.form["txtMatriculaFA"]
    nombreapellido = request.form["txtNombreApellidoFA"]
    return f"Matrícula: {matricula} Nombre y Apellido: {nombreapellido}"

@app.route("/registrar", methods=["GET"])
def registrar():
    args = request.args
    con = get_db_connection()
    cursor = con.cursor()
    
    sql = "INSERT INTO sensor_log (Temperatura, Humedad, Fecha_Hora) VALUES (%s, %s, %s)"
    val = (args["temperatura"], args["humedad"], datetime.datetime.now(pytz.timezone("America/Matamoros")))
    cursor.execute(sql, val)
    con.commit()
    con.close()

    pusher_client.trigger("registrosTiempoReal", "registroTiempoReal", args)
    return jsonify(args)

@app.route("/buscar")
def buscar():
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM tst0_contacto ORDER BY Id_Contacto DESC")
    registros = cursor.fetchall()
    con.close()

    registros_list = [{"Id_Contacto": r[0], "Correo_Electronico": r[1], "Nombre": r[2], "Asunto": r[3]} for r in registros]
    return jsonify(registros_list)

@app.route("/contacto", methods=["GET", "POST"])
def contacto():
    if request.method == "POST":
        correo = request.form["email"]
        nombre = request.form["nombre"]
        asunto = request.form["asunto"]
        
        print(f"Correo: {correo}, Nombre: {nombre}, Asunto: {asunto}")

        con = get_db_connection()
        cursor = con.cursor()
        sql = "INSERT INTO tst0_contacto (Correo_Electronico, Nombre, Asunto) VALUES (%s, %s, %s)"
        val = (correo, nombre, asunto)
        cursor.execute(sql, val)
        con.commit()
        con.close()

        pusher_client.trigger("registrosTiempoReal", "registroTiempoReal", {"email": correo, "nombre": nombre, "asunto": asunto})
    
    return render_template("contacto.html")

if __name__ == "__main__":
    app.run(debug=True)
@app.route("/guardar", methods=["POST"])
def guardar():
    if not con.is_connected():
        con.reconnect()

    id          = request.form["id"]
    temperatura = request.form["temperatura"]
    humedad     = request.form["humedad"]
    fechahora   = datetime.datetime.now(pytz.timezone("America/Matamoros"))
    
    cursor = con.cursor()

    if id:
        sql = """
        UPDATE sensor_log SET
        Temperatura = %s,
        Humedad     = %s
        WHERE Id_Log = %s
        """
        val = (temperatura, humedad, id)
    else:
        sql = """
        INSERT INTO sensor_log (Temperatura, Humedad, Fecha_Hora)
                        VALUES (%s,          %s,      %s)
        """
        val =                  (temperatura, humedad, fechahora)
    
    cursor.execute(sql, val)
    con.commit()
    con.close()

    notificarActualizacionTemperaturaHumedad()

    return make_response(jsonify({}))

@app.route("/editar", methods=["GET"])
def editar():
    if not con.is_connected():
        con.reconnect()

    id = request.args["id"]

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT Id_Log, Temperatura, Humedad FROM sensor_log
    WHERE Id_Log = %s
    """
    val    = (id,)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()

    return make_response(jsonify(registros))

@app.route("/eliminar", methods=["POST"])
def eliminar():
    if not con.is_connected():
        con.reconnect()

    id = request.form["id"]

    cursor = con.cursor(dictionary=True)
    sql    = """
    DELETE FROM sensor_log
    WHERE Id_Log = %s
    """
    val    = (id,)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    notificarActualizacionTemperaturaHumedad()

    return make_response(jsonify({}))
