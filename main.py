import detect
import recognize
import asyncio
import queue
import threading

# TODO: 
# Real-time face detection and recognition
# Optimize face recognition timings for faster processing when having too much users
# encrypt face data
# put hash/byte comparison or any other form to ensure the face is indeed registered for that user and in database


async def realtime(frame_queue, face_encodings, names):
    while True:
        frame = await asyncio.get_event_loop().run_in_executor(None, frame_queue.get)
        
        results = []
        try:
            results = list(recognize.who(frame,face_encodings,names))
        except:
            pass
        
        print(results)
        
        await asyncio.sleep(2)

async def webcam(*args):
    frame_queue = queue.Queue()

    capture_thread = threading.Thread(target=detect.capture_webcam, args=(frame_queue,))
    capture_thread.start()

    try:
        await realtime(frame_queue, *args)
    except asyncio.CancelledError:
        capture_thread.join()

if __name__ == "__main__":
    face_encodings, names = recognize.encode_faces()
    
    asyncio.run(webcam(face_encodings,names))
    
# cv2.putText(image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)