import detection
import recognize
import asyncio
import queue
import threading
from encryption import encryption, credentials
import json

# TODO: 
# Optimize face recognition timings for faster processing when having too much users
# encrypt face data
# put hash/byte comparison or any other form to ensure the face is indeed registered for that user and in database

async def camera(face_encodings, names, show=False, rtsp=False, register: bool = False, username: str = None):
    frame_queue = queue.Queue()

    if register == True:
        cam = detection.Camera(register=True, recognize=False)
    else:
        cam = detection.Camera(register=False,recognize=True)

    if rtsp:
        capture_thread = threading.Thread(target=cam.ip_camera, args=("admin","admin","192.168.0.102","1935","1",)) # change with your rtsp credentials, ip, port and stream source
        capture_thread.start()
    else:
        capture_thread = threading.Thread(target=cam.webcam, args=(1,)) # change your camera source here
        capture_thread.start()
    
    await asyncio.sleep(5)

    if not register:
        detection_thread = threading.Thread(target=cam.detect, args=(frame_queue,))
    elif register and not username:
        raise KeyError("Missing username for register")
    else:
        detection_thread = threading.Thread(target=cam.detect, args=(frame_queue,))
    detection_thread.start()

    if show:
        video_thread = threading.Thread(target=cam.show)
        video_thread.start()

    if register == False:
        try:
            await recognize.realtime_recognition(frame_queue, face_encodings, names)
        except asyncio.CancelledError:
            capture_thread.join()
            detection_thread.join()
            if show:
                video_thread.join()
                
    else:
        try:
            frame = await asyncio.get_event_loop().run_in_executor(None, frame_queue.get)
            
            keys = credentials().generate_keys()
            
            # keys_base64 = encryption().keys_base64(keys)
            
            fernet = encryption().gen_multi_fernet(keys)
            
            image = detection.encode_frame(frame)
            
            encrypted_image = encryption().encrypt_image(fernet=fernet,image=image)
            
            with open(f"./known_users/{username}.jpg", 'wb') as face:
                face.write(encrypted_image)
                
            with open(f"./users_keys/{username}.key", "w") as keys_file:
                json.dump(keys,keys_file)
            
        except asyncio.CancelledError:
            capture_thread.join()
            detection_thread.join()
            if show:
                video_thread.join()

if __name__ == "__main__":
    face_encodings, names = recognize.encode_faces()
    
    asyncio.run(camera(face_encodings,names,True,False,False,"Snootic"))
    