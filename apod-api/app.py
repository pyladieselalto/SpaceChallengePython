# Importamos las bibliotecas necesarias
from flask import Flask, render_template, jsonify, request
import requests
from datetime import date
from deep_translator import GoogleTranslator
from decouple import config

# Creamos una instancia de la aplicación Flask
app = Flask(__name__)

# Obtenemos la fecha actual en formato ISO
fecha_max = date.today().isoformat()

# Definimos una ruta para la página principal
@app.route('/')
def main():
    return render_template('index.html', fecha_max=fecha_max)

# Definimos una ruta para la página que muestra datos para una fecha seleccionada
@app.route('/day', methods=['GET', 'POST'])
def day():
    if request.method == 'POST':
        # Obtenemos la fecha seleccionada desde el formulario
        fecha_seleccionada = request.form['fecha']
        # Verificamos si la fecha seleccionada es mayor que la fecha máxima permitida
        if fecha_seleccionada > fecha_max:
            return render_template('day.html', error="La fecha no es correcta")
        else:
            # Construimos la URL para hacer una solicitud a una API 
            url = f"{config('API_URL')}?api_key={config('API_KEY')}&date={fecha_seleccionada}"
            # Realizamos una solicitud GET a la API 
            response = requests.get(url)
            if response.status_code == 200:
                # La solicitud fue exitosa
                data = response.json()
                # Creamos una copia del diccionario original
                datos_traducidos = data.copy()
                # Traducimos el campo 'explanation' y asignamos a la copia
                datos_traducidos['explanation'] = GoogleTranslator(source='en', target='es').translate(data['explanation'])
                # Traducimos el título
                titulo = GoogleTranslator(source='en', target='es').translate(data['title'])
                # Renderizamos la plantilla HTML con los datos y la fecha seleccionada
                return render_template('day.html', fecha_seleccionada=fecha_seleccionada, data=datos_traducidos, titulo=titulo)
            else:
                # La solicitud falló, mostrar un mensaje de error con el código de estado
                error = f"Error en la solicitud. Código de estado: {response.status_code}"
                return render_template('day.html', fecha_seleccionada=fecha_seleccionada, error=error)

# Ejecutamos la aplicación 
if __name__ == '__main__':
    app.run(debug=True)