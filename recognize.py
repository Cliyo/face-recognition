import face_recognition
import os
import asyncio
from encryption import encryption
import json
from io import BytesIO

def encode_faces():
    known_faces = os.listdir("./known_users")

    known_face_encodings = []
    known_face_names = []
    
    allowed_files = ["png","jpg","jpeg","gif"]

    for face in known_faces:
        face_name = f"{face}".split(".")
        if face_name[1] not in allowed_files:
            continue
        face_name = face_name[0]
        
        with open(f"./users_keys/{face_name}.key", "r") as keys_file:
            keys = json.load(keys_file)
        
        with open(f"./known_users/{face}", "rb") as image_file:
            image_bytes = image_file.read()
            
        # keys = encryption().encode_keys(keys_base64)
            
        fernet = encryption().gen_multi_fernet(keys)
        
        bytes_file = encryption().decrypt_image(fernet,image_bytes)
        
        file = BytesIO(bytes_file)
        
        face_image = face_recognition.load_image_file(file)
        
        try:
            face_image_encoding = face_recognition.face_encodings(face_image)[0]
            known_face_encodings.append(face_image_encoding)
            known_face_names.append(face_name)
        except:
            print(f"Não foi possivel encontrar rostos na imagem {face}")
    
    return known_face_encodings, known_face_names

def who(image,known_face_encodings,known_face_names):
    face_location = face_recognition.face_locations(image)
    face_encoding = face_recognition.face_encodings(image, face_location)

    for (top, right, bottom, left), face_encoding in zip(face_location, face_encoding):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.49)

        result = False
        
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
            result = True
            
        return result, name

async def realtime_recognition(frame_queue, face_encodings, names):
    while True:
        frame = await asyncio.get_event_loop().run_in_executor(None, frame_queue.get)
        
        results = []
        try:
            results = list(who(frame,face_encodings,names))
        except Exception as e:
            print(e)
            
        print(results)
        
        await asyncio.sleep(2)