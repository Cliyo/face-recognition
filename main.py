import detect
import recognize

# TODO: 
# Real-time face detection and recognition
# Optimize face recognition timings for faster processing when having too much users
# encrypt face data
# put hash/byte comparison or any other form to ensure the face is indeed registered for that user and in database

unknown_image = detect.read_image("./pictures/user2_1.jpeg")

face_encodings, names = recognize.encode_faces()

results = list(recognize.who(unknown_image,face_encodings,names))

print(results)

# cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)

# cv2.putText(image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

# scale_percent = 25
# width = int(unknown_image.shape[1] * scale_percent / 100)
# height = int(unknown_image.shape[0] * scale_percent / 100)
# new_dimensions = (width, height)

# unknown_image = cv2.resize(unknown_image, new_dimensions, interpolation=cv2.INTER_AREA)

# cv2.imshow('Result', unknown_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()