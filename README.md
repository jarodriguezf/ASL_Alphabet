<h1 align="center"> ASL Alphabet </h1>

![portada_IA](https://github.com/jarodriguezf/ASL_Alphabet/assets/112967594/4a9f3327-d0a8-40b7-b6e3-552d78af7b2e)

<h2> Descripcion del proyecto</h2>

La funcionalidad general de la aplicacion es la de detectar los gestos de lenguaje de signos (americano).

El modelo de deteccion infiere la posicion así como las señas mostradas (de una mano) devolviendo el resultado
como una cadena de texto. Permitiendo poder escribir letras, espacios y eliminar caracteres, tal y como lo hacemos en un editor de texto.

El proyecto se ha realizado con fines didacticos, por tanto, no esta desarrollado con funcionalidades para el uso profesional.


<h2>Video de muestra</h2>

  

https://github.com/jarodriguezf/ASL_Alphabet/assets/112967594/72c42bae-223f-4aa6-94dd-c3057e0fc0f0


- Ejemplo de gestos que podemos realizar:
  
![gestos_ejemplos](https://github.com/jarodriguezf/ASL_Alphabet/assets/112967594/6944ecc3-b4a4-48af-9320-ce0a5aef27a3)


<h2>Acceso al proyecto</h2>

El proyecto se encuentra en la carpeta --> 📁 ASl_Api_Web.

![image](https://github.com/jarodriguezf/ASL_Alphabet/assets/112967594/67b32687-a4d6-496f-9a51-c31682254a2f)

- Dentro de esta carpeta nos encontraremos dos ficheros llamados --> main.py, gesture_recognizer.task.
- Estos dos ficheros pertenecen a la api (main.py) y al modelo entrenado (gesture_recognizer.task).
![image](https://github.com/jarodriguezf/ASL_Alphabet/assets/112967594/0fac1223-78d0-48bc-a2a7-96815f4652e5)

- Además, dentro de ASl_Api_Web, encontramos una carpeta llamada --> static. Esta carpeta alberga el index.html
![image](https://github.com/jarodriguezf/ASL_Alphabet/assets/112967594/fb22f13c-21b3-402d-ab50-b1c7b022a5a9)



<h3>🛠️<b>Para ejecutar el proyecto solo es necesario hacer uso del directorio especificado arriba (ASL_Api_Web).</b></h3>

  - necesitaremos instalar las librerias de Mediapipe, opencv y fastApi si no las tenemos.
  
  - Una vez hecho esto, arrancaremos el servidor (main.py) y luego escribiremos en nuestro navegador (http://127.0.0.1:5500/static/index.html).
    
  - Esperaremos a que la camara (utiliza la predeterminada del dispositivo) se active y ya podremos empezar a realizar las señas para su deteccion.


<i>El resto de los archivos de ASL_Alphabet, corresponden a analisis de datos, baseline con las primeras predicciones, 
dos modelos entrenados con diferentes tamaños de informacion y un script que ejecuta la prediccion sin la api.</i>


<h2>✔️ Tecnologias usadas</h2>

- Python 3.11
- MediaPipe
- TensorFlow
- Lenguajes tipicos para desarrollo web (html,css,js)
- FastAPI



