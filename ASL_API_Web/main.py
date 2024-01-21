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


def print_result(result, output_image, timestamp_ms):
    global concatenated_names
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

def perform_gesture_recognition(recognizer, frame, last_inference_time):
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    current_time = time.time()

    # Perform gesture recognition every 5 seconds
    if current_time - last_inference_time >= 5.0:
        # Update last inference time
        last_inference_time = current_time

        # Perform gesture recognition asynchronously
        recognizer.recognize_async(mp_image, timestamp_ms=int(current_time * 1000))

    return last_inference_time


# Inicializar el reconocedor de gestos de mediapipe
model_path = 'gesture_recognizer.task'
base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Gesture Recognizer Options Setup
options = GestureRecognizerOptions(
base_options=base_options,
running_mode=VisionRunningMode.LIVE_STREAM,
result_callback=print_result)

recognizer = GestureRecognizer.create_from_options(options)

async def send_data_to_clients(data):
    json_data = {"Message": data}
    for ws in set(active_websockets):
        try:
            await ws.send_json(json_data)
        except WebSocketDisconnect:
            active_websockets.remove(ws)

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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.add(websocket)

    try:
        await process_video_capture(websocket)
    except WebSocketDisconnect:
        active_websockets.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")