# Importamos las bibliotecas necesarias
from flask import Flask, render_template, jsonify
import requests
from decouple import config

# Creamos una instancia de la aplicación Flask
app = Flask(__name__)

# Ruta principal que muestra la página de inicio
@app.route('/')
def main():
    return render_template('index.html')  

# Ruta para obtener datos de los rovers desde la API 
@app.route('/rovers', methods=['GET'])
def rovers():
    url = f"{config('API_URL')}?api_key={config('API_KEY')}"
    # Realizamos una solicitud GET a la API 
    response = requests.get(url)
    if response.status_code == 200:
        # Si la solicitud fue exitosa, obtiene los datos de los rovers en formato JSON
        rover_data = response.json()  
        # Renderizamos la plantilla "rovers.html" pasando los datos de los rovers
        return render_template('rovers.html', data=rover_data['rovers'])  
    else:
        # Si la solicitud falló, devuelve un JSON de error con un código de estado HTTP 500
        return jsonify({'error': f"Error en la solicitud. Código de estado: {response.status_code}"}), 500

# Ruta para obtener fotos de un rover específico y una cámara específica en un día específico (Sol)
@app.route('/camera/<rover_name>/<max_sol>/<camera_name>/', methods=['GET'])
def camera(rover_name, max_sol, camera_name):
    sol_pic = False  # Bandera para verificar si se ha encontrado una foto para el día dado (Sol).
    sol = int(max_sol)  # Convertimos la entrada max_sol a un entero para usarlo en la solicitud.
    retry_count = 0  # Contador de reintentos en caso de que no se encuentren fotos.

    #Ejecutamos este bucle hasta que se encuentre una foto o se agoten los reintentos.
    while not sol_pic:
        # Construimos la URL de la solicitud a la API de la NASA utilizando los parámetros proporcionados.
        url = f"{config('API_URL')}{rover_name}/photos?sol={sol}&camera={camera_name}&api_key={config('API_KEY')}"
        print(url)  # Imprimimos la URL en la consola para fines de depuración.

        # Realizamos una solicitud GET a la URL para obtener datos de fotos del rover y la cámara en el día (Sol) dado.
        response = requests.get(url)

        # Comprobamos si la solicitud fue exitosa (código de estado 200).
        if response.status_code != 200:
            # Si la solicitud no fue exitosa, muestra un mensaje de error y devuelve una respuesta JSON con un código de estado 500.
            print(f"Error {response.status_code} while fetching photos for rover {rover_name} on Sol {sol} with camera {camera_name}")
            return jsonify({'error': f"Error en la solicitud. Código de estado: {response.status_code}"}), 500

        # Convertimos la respuesta JSON en un diccionario de Python llamado 'data'.
        data = response.json()

        # Verificamos si se encontraron fotos en la respuesta o si se ha superado el número máximo de reintentos (2).
        if data['photos'] or retry_count > 2:
            sol_pic = True  # Se encontraron fotos o se superó el límite de reintentos.
        else:
            sol -= 1  # Reducimos el número de Sol en 1 para intentar buscar fotos en un día anterior.
            retry_count += 1  # Incrementamos el contador de reintentos.
    
    # Renderizamos la plantilla "camera.html" pasando los datos de las fotos
    return render_template('camera.html', data=data['photos']) 

# Ejecutamos la aplicación 
if __name__ == '__main__':
    app.run(debug=True)