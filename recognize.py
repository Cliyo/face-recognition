import face_recognition
import os

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
        face_image = face_recognition.load_image_file(f"./known_users/{face}")
        face_image_encoding = face_recognition.face_encodings(face_image)[0]
        known_face_encodings.append(face_image_encoding)
        known_face_names.append(face_name)

    
    return known_face_encodings, known_face_names

def who(image,known_face_encodings,known_face_names):
    face_location = face_recognition.face_locations(image)
    face_encoding = face_recognition.face_encodings(image, face_location)

    for (top, right, bottom, left), face_encoding in zip(face_location, face_encoding):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        result = False
        
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
            result = True
            
        return result, name

