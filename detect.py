import cv2
from time import sleep, time
import numpy as np

def read_image(image_path):
    image = cv2.imread(image_path)
    
    scale_percent = 30
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    new_dimensions = (width, height)
    
    image = cv2.resize(image, new_dimensions, interpolation=cv2.INTER_AREA)
    
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    # faces = face_cascade.detectMultiScale(image, 1.1, 4)

    # for (x, y, w, h) in faces:
    #     cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return image_rgb

def capture_webcam(frame_queue,camera_index=0):
    image = cv2.VideoCapture(camera_index)
    cv2.namedWindow("test")

    last_frame_time = time()

    while True:
        ret, frame = image.read()
        if not ret:
            print("failed to grab frame")
            break
        
        frame = cv2.resize(frame, (640,480))
        
        top_left, bottom_right = draw_face_frame(frame)
        
        face_frame = frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        
        frame_marked = face_frame.copy()

        if is_low_light(face_frame, threshold=70):
            cv2.putText(frame_marked, "Low Light", (top_left[0]-150, top_left[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(face_frame, 1.05, 6)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame_marked, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            face_frame_rgb = cv2.cvtColor(face_frame, cv2.COLOR_BGR2RGB)
            
            if len(faces) == 1 and time() - last_frame_time > 3:
                last_frame_time = time()
                print("Face found")
                frame_queue.put(face_frame_rgb)
        
        cv2.imshow("test", frame_marked)
        cv2.waitKey(1)
        
        sleep(1/5)

    image.release()


def camera_over_internet():
    pass


def is_low_light(image, threshold=50):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_intensity = np.mean(gray)
    return mean_intensity < threshold

def draw_face_frame(frame):
    height, width, _ = frame.shape
    top_left = (int(width * 0.25), int(height * 0.05))
    bottom_right = (int(width * 0.75), int(height * 0.9))
    cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
    return top_left, bottom_right