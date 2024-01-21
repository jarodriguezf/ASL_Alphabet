import cv2
import mediapipe as mp
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocketDisconnect, WebSocketState
import time

app = FastAPI()

# Configurar la carpeta para archivos estáticos (por ejemplo, HTML, JS, CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Almacena las conexiones WebSocket activas
active_websockets = set()

# FUncion que maneja y extrae la cetegoria de la lista (resultado)
def concatenate_gesture_names(result):

    current_names = ""  # Variable local para contener los nombres de los gestos actuales
    if result.gestures:
        for gesture in result.gestures:
            if isinstance(gesture, list):
                for sub_gesture in gesture:
                    try:
                        category_name = sub_gesture.category_name
                        current_names += category_name
                    except AttributeError as e:
                        print(f"Error processing gesture: {e}")
                        print(f"Type of exception: <class 'AttributeError'>")
            else:
                try:
                    category_name = gesture.category_name
                    current_names += category_name
                except AttributeError as e:
                    print(f"Error processing gesture: {e}")
                    print(f"Type of exception: <class 'AttributeError'>")
    return current_names

# Captura el resultado que es manejado como una lista de listas.
def print_result(result, output_image, timestamp_ms):
    global concatenated_names
    # La lista pasa a la siguiente funcion, que se encarga de navegar por ella hasta acceder a la categoria indicada.
    current_names = concatenate_gesture_names(result)

    if current_names:
        if current_names == 'space':
            concatenated_names += ' '
        elif current_names == 'del':
            concatenated_names = concatenated_names[:-1]  
        else:
            concatenated_names += current_names
    else:
        print('No gestures detected')


# Funcion que controla la inferencia del modelo predictivo cada 5 segundos.
def perform_gesture_recognition(recognizer, frame, last_inference_time):
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    current_time = time.time()

    # Comprueba si el tiempo actual es mayor que 5 segundos
    if current_time - last_inference_time >= 5.0:
        # Actualiza el ultimo tiempo con el actual
        last_inference_time = current_time

        # Envia el frame a traves del objeto recognizer para su prediccion,
        # devolviendo el resultado en la funcion print_result().
        recognizer.recognize_async(mp_image, timestamp_ms=int(current_time * 1000))

    return last_inference_time


# Las siguientes lineas, inicializa el reconocedor de gestos de mediapipe (se crea una vez al arrancar el servidor)
# Cargamos las instancias necesarias de mediapipe
model_path = 'gesture_recognizer.task'
base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Configuramos el objeto recognizer antes de crearlo, gracias a las instancias cargadas anteriormente, 
# el recognizer es el objeto encargado de inferir los gestos
options = GestureRecognizerOptions(
base_options=base_options,
running_mode=VisionRunningMode.LIVE_STREAM,
result_callback=print_result)
# Objeto recognizer (configurado con la opciones de arriba)
recognizer = GestureRecognizer.create_from_options(options)

# Funcion que maneja el resultado de la inferencia, en un JSON manejado por websocket
async def send_data_to_clients(data):
    json_data = {"Message": data}
    for ws in set(active_websockets):
        try:
            await ws.send_json(json_data)
        except WebSocketDisconnect:
            active_websockets.remove(ws)


# Funcion que captura en bucle los frames de la camara, los envia al modelo predictivo y retorna el resultado al cliente.
async def process_video_capture(websocket: WebSocket):
    global active_websockets, concatenated_names
    concatenated_names = ""
    
    cap = cv2.VideoCapture(0)
    last_inference_time = time.time()

    try:
        while cap.isOpened() and websocket.application_state != WebSocketState.DISCONNECTED:
            ret, frame = cap.read()
            if not ret:
                break

            # Realizar el procesamiento de gestos con Mediapipe
            last_inference_time = perform_gesture_recognition(recognizer, frame, last_inference_time)

            # Enviar resultados a los clientes WebSocket si la conexión aún está abierta
            if websocket.application_state != WebSocketState.DISCONNECTED:
                await send_data_to_clients(concatenated_names)

                # Enviar el fotograma al cliente
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                await websocket.send_bytes(frame_bytes)
        # Restablecer la variable concatenated_names después de enviar datos a los clientes
        concatenated_names = ""
    except WebSocketDisconnect:
        pass
    finally:
        cap.release()
        active_websockets.remove(websocket)

# Endpoint que crea el websocket y llama a iniciar la videocamara
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.add(websocket)

    try:
        await process_video_capture(websocket)
    except WebSocketDisconnect:
        active_websockets.remove(websocket)

# Host por el que se ejecuta el servidor
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")