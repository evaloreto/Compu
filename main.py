from flask import Flask, render_template, request, redirect
import re
from beebotte import *
import time
import requests
from pymongo import MongoClient
import locale


app = Flask(__name__)

leer_bbdd_interna = True

@app.route('/')
def main():
    return render_template('main.html')


@app.route('/result', methods=['GET', 'POST'])
def result():
    global leer_bbdd_interna
    locale.setlocale(locale.LC_TIME, 'es_ES')

    # Conexion con BBDD interna
    # Por defecto la base de datos de mongo usa el puerto 27017
    client = MongoClient()
    # Asignamos la base de datos a una variable BD: numeros
    db = client.numeros

    # Conexion con BBDD externa
    _accesskey = 'e64705459c40abbfe3e8c0b09cb14acf'
    _secretkey = '42199826e66579c6c62b56f4231a9126ed832364113b83d02731d0b2f75fc01f'
    _hostname = 'api.beebotte.com'
    bbt = BBT(_accesskey, _secretkey, hostname=_hostname)

    # Inicializamos valormedio, para que no de error en caso de que no se use
    valormedio = -1.0

    if request.method == "GET":
        web_num_aleatorio = requests.get('http://www.numeroalazar.com.ar/')
        if web_num_aleatorio.status_code == 200:
            r = re.compile(r'..meros\sgenerados</h2>.(.*?)<br>', re.DOTALL)
            m = r.search(web_num_aleatorio.text)
            if m:
                num_busqueda = re.search("\d+(?:\.\d+)?", m.group(1))
                num = float(num_busqueda.group())
                hora_busqueda = time.strftime("%H:%M:%S")
                fecha_busqueda = time.strftime("%x")

                # Dentro de la BBDD interna, guardamos colecciones de archivos (que son los que contienen toda la informacion de un
                # numero. Usaremos una coleccion que se llame aleatorios
                db.aleatorios.insert_one(
                    {
                        "valor": num,
                        "fecha": fecha_busqueda,
                        "hora": hora_busqueda
                    }
                )
                # Guardamos tambien en la BBDD externa, en el canal numeros y cada variable en su recurso
                bbt.write("numeros", "valor", num)
                bbt.write("numeros", "fecha", fecha_busqueda)
                bbt.write("numeros", "hora", hora_busqueda)

                query = db.aleatorios.find()
    elif request.method == "POST":
        calc_valormedio = request.form.get('valormedio', default=False, type=bool)
        print calc_valormedio
        umbral = request.form.get('umbral', default=-1, type=int)
        if umbral == -1:
            query = list(db.aleatorios.find())
            if calc_valormedio:
                total_valores = 0
                valormedio = 0.0
                if leer_bbdd_interna:
                    for document in query:
                        valormedio = valormedio + float(document['valor'])
                        total_valores = total_valores + 1
                else:
                    query_externa = bbt.read("numeros", "valor", limit=50000)
                    for valor in query_externa:
                        valormedio = valormedio + valor['data']
                        total_valores = total_valores + 1

                valormedio = valormedio / total_valores
                leer_bbdd_interna = not leer_bbdd_interna
            else:
                query = db.aleatorios.find()
        else:
            query = list(db.aleatorios.find({'valor': {'$gt': umbral}}))
            if calc_valormedio:
                total_valores = 0
                valormedio = 0.0
                if leer_bbdd_interna:
                    for document in query:
                        valormedio = valormedio + float(document['valor'])
                        total_valores = total_valores + 1
                else:
                    query_externa = bbt.read("numeros", "valor", limit=50000)
                    for valor in query_externa:
                        if valor['data'] > umbral:
                            valormedio = valormedio + valor['data']
                            total_valores = total_valores + 1

                valormedio = valormedio / total_valores
                leer_bbdd_interna = not leer_bbdd_interna
            else:
                query = db.aleatorios.find({'valor': {'$gt': umbral}})

    return render_template('result.html', query=query, valormedio=valormedio, bbdd=leer_bbdd_interna)


@app.route('/graficas_externas', methods=['GET'])
def graficas_externas():
    return redirect("https://beebotte.com/dash/d2c310e0-d208-11e7-bfef-6f68fef5ca14", code=302)

