from flask import Flask
from markupsafe import escape

from flask import render_template
from flask import request

import pusher

import mysql.connector
import datetime
import pytz

con = mysql.connector.connect(
  host="185.232.14.52",
  database="u760464709_tst_sep",
  user="u760464709_tst_sep_usr",
  password="dJ0CIAFF="
)

app = Flask(__name__)

@app.route("/")
def index():
    con.close()
  
    return render_template("app.html")

@app.route("/alumnos")
def alumnos():
    con.close()
  
    return render_template("alumnos.html")

@app.route("/alumnos/guardar", methods=["POST"])
def alumnosGuardar():
    con.close()
  
    matricula      = request.form["txtMatriculaFA"]
    nombreapellido = request.form["txtNombreApellidoFA"]

    return f"Matrícula: {matricula} Nombre y Apellido: {nombreapellido}"

@app.route("/registrar", methods=["GET"])
def registrar():
    args = request.args
    pusher_client = pusher.Pusher(
        app_id='1864237',
        key='fe0a6fda0635d4db01ce',
        secret='e5c4c8f921f883404989',
        cluster='us2',
        ssl=True
    )

    if not con.is_connected():
        con.reconnect()
    cursor = con.cursor()
    
    sql = "INSERT INTO sensor_log (Temperatura, Humedad, Fecha_Hora) VALUES (%s, %s, %s)"
    val = (args["temperatura"], args["humedad"], datetime.datetime.now(pytz.timezone("America/Matamoros")))
    cursor.execute(sql, val)

    con.commit()
    con.close()
 
    pusher_client.trigger("registrosTiempoReal", "registroTiempoReal", args)
    return args

@app.route("/buscar")
def buscar():
    if not con.is_connected():
        con.reconnect()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM sensor_log ORDER BY Id_Log DESC")
    registros = cursor.fetchall()

    con.close()

    return registros

@app.route("/contacto", methods=["GET", "POST"])
def contacto():
    if request.method == "POST":
        correo = request.form["email"]
        nombre = request.form["nombre"]
        asunto = request.form["asunto"]

        # Verificamos la conexión antes de ejecutar consultas
        if not con.is_connected():
            con.reconnect()

        cursor = con.cursor()
        sql = "INSERT INTO contactos (Correo_Electronico, Nombre, Asunto) VALUES (%s, %s, %s)"
        val = (correo, nombre, asunto)
        cursor.execute(sql, val)

        con.commit()
        cursor.close()

        return redirect(url_for("exito"))
    
    return render_template("contacto.html")

@app.route("/exito")
def exito():
    return "Gracias por contactarnos. Hemos recibido tu información."

if __name__ == "__main__":
    app.run(debug=True)
