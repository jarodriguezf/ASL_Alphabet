import cv2
import mediapipe as mp
import time

concatenated_names = ""  # Declarar fuera de la función para mantener el estado

def concatenate_gesture_names(result):
    global concatenated_names
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

        print(concatenated_names)
    else:
        print('No gestures detected')
    print('=========================================================')



def initialize_gesture_recognition(model_path):
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
    return recognizer

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

def main():
    model_path = '../../../gesture_recognizer.task'
    recognizer = initialize_gesture_recognition(model_path)

    cap = cv2.VideoCapture(0)  # 0 for default camera, you can change it if needed
    last_inference_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        last_inference_time = perform_gesture_recognition(recognizer, frame, last_inference_time)

        cv2.imshow('Frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()