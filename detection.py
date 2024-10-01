import cv2
from time import sleep, time
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
FaceDetectorResult = mp.tasks.vision.FaceDetectorResult
VisionRunningMode = mp.tasks.vision.RunningMode

def read_image(image_path):
    image = cv2.imread(image_path)
    
    scale_percent = 30
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    new_dimensions = (width, height)
    
    image = cv2.resize(image, new_dimensions, interpolation=cv2.INTER_AREA)
    
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return image_rgb

class Camera():
    def __init__(self,register=False, recognize=False):
        self.image = None
        self.ret = None
        self.frame = None
        
        self.frame_marked = None
        self.face_frame = None
        self.face_frame_rgb = None
        self.frame_queue = None
        
        self.register = register
        self.recognize = recognize
        self.framerate = 1/8
        self.recognise_frame_time = time()
    
    def capture(self, source, **kwargs):
        if source == "rtsp":
            rtsp_user = kwargs.get('rtsp_user')
            rtsp_password = kwargs.get('rtsp_password')
            camera_ip = kwargs.get('camera_ip')
            port = kwargs.get('port')
            stream_source = kwargs.get('stream_source')
            
            if not all([rtsp_user, rtsp_password, camera_ip, port, stream_source]):
                raise ValueError("Missing required RTSP parameters.")
            
            rtsp_url = f"rtsp://{rtsp_user}:{rtsp_password}@{camera_ip}:{port}/{stream_source}"
            self.image = cv2.VideoCapture(rtsp_url)
        
        else:
            self.image = cv2.VideoCapture(source)

        self.ret, self.frame = self.image.read()
        if not self.ret:
            print("Failed to grab frame")
            self.image = None
            return None

    def webcam(self, camera_index=0):
        self.capture(camera_index)

    def ip_camera(self, rtsp_user, rtsp_password, camera_ip, port, stream_source):
        self.capture("rtsp", rtsp_user=rtsp_user, rtsp_password=rtsp_password, 
                            camera_ip=camera_ip, port=port, stream_source=stream_source)

    def show(self):
        if not self.image:
            raise ValueError("please, start the camera first")
        cv2.namedWindow("test")
        while True:
            if self.frame_marked is not None:
                cv2.imshow("test", self.frame_marked)
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
        cv2.destroyAllWindows()

    def handle_detection(self, result: FaceDetectorResult, output_image: mp.Image, timestamp_ms: int):            
        for face in result.detections:
            bounding_box = face.bounding_box
            cv2.rectangle(self.frame_marked, (bounding_box.origin_x, bounding_box.origin_y), (bounding_box.origin_x+bounding_box.width, bounding_box.origin_y+bounding_box.height), (255, 0, 0), 2)
        
        if self.recognize and (len(result.detections) == 1 and time() - self.recognise_frame_time > 3):    
            self.recognise_frame_time = time()
            print("Face found")
            self.frame_queue.put(self.face_frame_rgb)
            
        elif self.register and len(result.detections) < 1:
            self.recognise_frame_time = time()
        
        elif self.register and (len(result.detections) == 1 and time() - self.recognise_frame_time > 5):
            print("beginning face registration, please do not move")
            
            cv2.imwrite(f"client_register.jpg", self.face_frame)
            
            self.frame_queue.put(self.face_frame)
            
            self.recognise_frame_time = time()
    
    def detect(self,frame_queue):
        if not self.image:
            raise ValueError("please, start the camera first")
        
        self.frame_queue = frame_queue
        
        last_frame_time = time()
        self.recognise_frame_time = time()
        
        if self.recognize and self.register:
            raise KeyError("both recognize and register params cannot be true at the same time")

        timestamp: int = 0
        
        mediapipe_base_options = python.BaseOptions(model_asset_path='blaze_face_short_range.tflite')
        options = vision.FaceDetectorOptions(base_options=mediapipe_base_options, running_mode=VisionRunningMode.LIVE_STREAM, result_callback = self.handle_detection)
        
        with vision.FaceDetector.create_from_options(options) as detector:
            while True:
                current_time = time()
                time_elapsed = current_time - last_frame_time
                
                if time_elapsed < self.framerate:
                    continue
                
                self.ret, self.frame = self.image.read()
                if not self.ret:
                    print("failed to grab frame")
                    break
                
                last_frame_time = current_time
                
                frame = cv2.resize(self.frame, (640,480))
                
                top_left, bottom_right = self.draw_face_frame(frame)
                
                self.face_frame = frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
                
                frame_marked = self.face_frame.copy()

                if not self.register and self.is_low_light(self.face_frame, threshold=70):
                    cv2.putText(frame_marked, "Low Light", (top_left[0]-150, top_left[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    
                elif self.register and self.is_low_light(self.face_frame, threshold=70):
                    cv2.putText(frame_marked, "Low Light", (top_left[0]-150, top_left[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    self.frame_marked = frame_marked.copy()
                    self.recognise_frame_time = time()
                    continue
                
                self.face_frame_rgb = cv2.cvtColor(self.face_frame, cv2.COLOR_BGR2RGB)
                
                image_to_detect = mp.Image(image_format=mp.ImageFormat.SRGB, data=self.face_frame_rgb)
                
                self.frame_marked = frame_marked.copy()
                
                detector.detect_async(image_to_detect, timestamp)
                timestamp += 1
                        
            self.image.release()

    def is_low_light(self,image, threshold=50):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_intensity = np.mean(gray)
        return mean_intensity < threshold

    def draw_face_frame(self,frame):
        height, width, _ = frame.shape
        top_left = (int(width * 0.25), int(height * 0.05))
        bottom_right = (int(width * 0.75), int(height * 0.9))
        cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
        return top_left, bottom_right
    
    def register_face(self, frame_queue):
        self.detect(frame_queue=frame_queue, register=True)
        
    def recognize_face(self, frame_queue):
        self.detect(frame_queue=frame_queue, recognize=True)