from flask import Flask, render_template, render_template,request,redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests
import json
from bs4 import BeautifulSoup


# Crea la conexión de la base de datos
def get_connection():
    try:
        client = MongoClient("mongodb+srv://jon_aguilar:EstudiantesMaestria2024.@cluster0.fe9drhr.mongodb.net/")
        return client
    except:
        print("Error")
        return None

#Indica el nombre de la base de datos
def get_database(db,client):
    try:
        mydb = client[db]
        return mydb
    except:
        return None

#Indica la tabla de base de datos
def get_schema(table,db):
    try:
        mycollection = db[table]
        return mycollection
    except:
        return None


app = Flask(__name__)

@app.route("/")
def home_page():
    cliente = get_connection()
    mydb = get_database("actividad_final_eq1", cliente)
    mydocuments = get_schema("Gizmodo", mydb)
    
    articulos = mydocuments.find()
    
    return render_template('index.html', articulos=articulos)

@app.route('/actualizar_encabezado', methods=['POST'])
def actualizar_encabezado():
    id_articulo = request.form['id']
    nuevo_titulo = request.form['nuevo_titulo']

    cliente = get_connection()
    mydb = get_database("actividad_final_eq1", cliente)
    mydocuments = get_schema("Gizmodo", mydb)

    # Actualizar el título en la base de datos
    result = mydocuments.update_one(
        {'_id': ObjectId(id_articulo)},
        {'$set': {'Encabezado': nuevo_titulo}}
    )

    if result.modified_count > 0:
        mensaje = "Título actualizado correctamente."
    else:
        mensaje = "No se pudo actualizar el título."

    return mensaje

@app.route('/eliminar_articulo/<string:id>', methods=['POST'])
def eliminar_articulo(id):
    cliente = get_connection()
    mydb = get_database("actividad_final_eq1", cliente)
    mydocuments = get_schema("Gizmodo", mydb)
    # Eliminar el artículo de la base de datos
    result = mydocuments.delete_one({'_id': ObjectId(id)})

    if result.deleted_count > 0:
        mensaje = "Artículo eliminado correctamente."
    else:
        mensaje = "No se pudo eliminar el artículo."
    return mensaje

@app.route('/restaurar_articulos', methods=['POST'])
def restaurar_articulos():
    url = "https://es.gizmodo.com/"
    response = requests.get(url)
    cliente = get_connection()
    mydb = get_database("actividad_final_eq1", cliente)
    mydocuments = get_schema("Gizmodo", mydb)
    # Verificar si la solicitud fue exitosa (código 200)
    if response.status_code == 200:
        # Elimina todos los registros actuales de la tabla.
        mydocuments.delete_many({})
        # Obtener el contenido HTML de la página
        html = response.text
        # Crear un objeto BeautifulSoup para analizar el HTML
        soup = BeautifulSoup(html, "html.parser")
        # Lista para almacenar los resultados
        results = []
        # Encontrar todos los elementos con la clase 'js_entry-title' quecontienen los títulos y enlaces de las noticias
        news_elements = soup.find_all(class_="sc-1pw4fyi-6 hGCNFC sc-1e59qvl-0 sc-1e59qvl-1 yrIlL gwBFdc js_post_item")
        # Iterar sobre los elementos y obtener los títulos, enlaces eimágenes de las noticias
        for news in news_elements:
            # Obtener el título de la noticia
            title = news.find('a')['title'] if news.find('a') else None
            # Obtener el enlace de la noticia
            link = news.find('a')['href'] if news.find('a') else None
            # Encontrar la etiqueta 'img' dentro del elemento
            image_tag = news.find("img")
            # Obtener el atributo 'src' que contiene la URL de la imagen
            image_url = image_tag["src"] if image_tag["src"] else None
            #Evaluamos si se ha obtenido un url válido
            if not image_url.startswith("http"):
                image_url = image_tag["data-src"] if image_tag["data-src"] else None
            # Crear un diccionario para almacenar los datos de la noticia
            news_data = {
                "Encabezado": title,
                "Enlace": link,
                "URLimagen": image_url
                }
            # Agregar los datos de la noticia a la lista de resultados
            results.append(news_data)
        # Imprimir los resultados en formato JSON
        # json_respuesta = json.dumps(results, indent=2, ensure_ascii=False)
        # Guardamos registros múltiples en BD
        resultado = mydocuments.insert_many(results)
        #multiples_registros = mydocuments.insert_many(results)
    else:
        print("Error al obtener la página:", response.status_code)
    return redirect('/')