import cv2
from time import sleep, time

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

def capture_webcam(frame_queue):
    image = cv2.VideoCapture(2)
    cv2.namedWindow("test")

    last_frame_time = time()

    while True:
        ret, frame = image.read()
        if not ret:
            print("failed to grab frame")
            break
        
        frame = cv2.resize(frame, (640,480))
        
        frame_marked = frame
        
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(cv2.cvtColor(frame_marked, cv2.COLOR_BGR2GRAY), 1.05, 6)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame_marked, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        if len(faces) == 1 and time() - last_frame_time > 3:
            last_frame_time = time()
            print("rosto encontrado")
            frame_queue.put(frame)
        
        # cv2.imshow("test", frame_marked)
        # cv2.waitKey(1)
        
        sleep(1/5)

    image.release()


def camera_over_internet():
    pass
