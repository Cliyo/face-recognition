import detection
import recognize
import asyncio
import queue
import threading

# TODO: 
# Optimize face recognition timings for faster processing when having too much users
# encrypt face data
# put hash/byte comparison or any other form to ensure the face is indeed registered for that user and in database

async def camera(face_encodings, names, show=None, rtsp=None):
    frame_queue = queue.Queue()

    cam = detection.Camera()

    if rtsp:
        capture_thread = threading.Thread(target=cam.ip_camera, args=("admin","admin","192.168.0.102","1935","1",)) # change with your rtsp credentials, ip, port and stream source
        capture_thread.start()
    else:
        capture_thread = threading.Thread(target=cam.webcam, args=(1,)) # change your camera source here
        capture_thread.start()
    
    await asyncio.sleep(5)

    detection_thread = threading.Thread(target=cam.detect, args=(frame_queue,))
    detection_thread.start()

    if show:
        video_thread = threading.Thread(target=cam.show)
        video_thread.start()

    try:
        await recognize.realtime_recognition(frame_queue, face_encodings, names)
    except asyncio.CancelledError:
        capture_thread.join()
        detection_thread.join()
        if show:
            video_thread.join()

if __name__ == "__main__":
    face_encodings, names = recognize.encode_faces()
    
    asyncio.run(camera(face_encodings,names,"show"))
    
# cv2.putText(image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)