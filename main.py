from flask import Flask, render_template
import re
import time
import requests
from pymongo import MongoClient

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/result', methods=['GET'])
def result():
    web_num_aleatorio = requests.get('http://www.numeroalazar.com.ar/')
    if web_num_aleatorio.status_code == 200:
        r = re.compile(r'..meros\sgenerados</h2>.(.*?)<br>', re.DOTALL)
        m = r.search(web_num_aleatorio.text)
        if m:
            num_busqueda = re.search("\d+(?:\.\d+)?", m.group(1))
            num = num_busqueda.group()
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

            query = db.aleatorios.find()
            for document in query:
                print document

            return num

