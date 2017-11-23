from flask import Flask, render_template, request
import re
import time
import requests
from pymongo import MongoClient

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/result', methods=['GET', 'POST'])
def result():
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

            if request.method == "GET":
                query = db.aleatorios.find()
            elif request.method == "POST":
                valormedio = request.form.get('valormedio', default=False, type=bool)
                umbral = request.form.get('umbral', default=-1, type=int)
                if umbral == -1:
                    query = db.aleatorios.find()
                else:
                    query = db.aleatorios.find({'valor': {'$gt': umbral}})
                    #for document in query:
                    #    print document['valor']

            #for document in query:
            #    print document['valor']
            #    print document['hora']
            #    print document['fecha']

        return render_template('results.html', query=query)