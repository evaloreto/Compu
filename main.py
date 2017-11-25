from flask import Flask, render_template, request
import re
import time
import requests
from pymongo import MongoClient
import locale

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/result', methods=['GET', 'POST'])
def result():
    locale.setlocale(locale.LC_TIME, 'es_ES')
    web_num_aleatorio = requests.get('http://www.numeroalazar.com.ar/')
    if web_num_aleatorio.status_code == 200:
        r = re.compile(r'..meros\sgenerados</h2>.(.*?)<br>', re.DOTALL)
        m = r.search(web_num_aleatorio.text)
        if m:
            num_busqueda = re.search("\d+(?:\.\d+)?", m.group(1))
            num = float(num_busqueda.group())
            hora_busqueda = time.strftime("%H:%M:%S")
            fecha_busqueda = time.strftime("%x")

            # Por defecto la base de datos de mongo usa el puerto 27017
            client = MongoClient()
            # Asignamos la base de datos a una variable BD: numeros
            db = client.numeros
            # Dentro de una BD, guardamos colecciones de archivos (que son los que contienen toda la informacion de un
            # numero. Usaremos una coleccion que se llame aleatorios
            db.aleatorios.insert_one(
                {
                    "valor": num,
                    "fecha": fecha_busqueda,
                    "hora": hora_busqueda
                }
            )

            # Inicializamos valormedio, para que no de error en caso de que no se use
            valormedio = -1.0

            if request.method == "GET":
                query = db.aleatorios.find()
            elif request.method == "POST":
                calc_valormedio = request.form.get('valormedio', default=False, type=bool)
                umbral = request.form.get('umbral', default=-1, type=int)
                if umbral == -1:
                    if calc_valormedio:
                        query = list(db.aleatorios.find())
                        total_valores = 0
                        valormedio = 0.0
                        for document in query:
                            valormedio = valormedio + float(document['valor'])
                            total_valores = total_valores + 1

                        valormedio = valormedio / total_valores
                    else:
                        query = db.aleatorios.find()
                else:
                    if calc_valormedio:
                        query = list(db.aleatorios.find({'valor': {'$gt': umbral}}))
                        total_valores = 0
                        valormedio = 0.0
                        for document in query:
                            valormedio = valormedio + float(document['valor'])
                            total_valores = total_valores + 1

                        valormedio = valormedio / total_valores
                    else:
                        query = db.aleatorios.find({'valor': {'$gt': umbral}})
                    #for document in query:
                    #    print document['valor']

            #for document in query:
            #   print document['valor']
            #    print document['hora']
            #    print document['fecha']

        return render_template('results.html', query=query, valormedio=valormedio)

    