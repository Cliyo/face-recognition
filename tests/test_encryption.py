from encryption import credentials, encryption
import os

def test_generate_keys():
    key = credentials().gen_decrypted_key()
    
def test_generate_token():
    fernet = credentials().generate_keys()
    
def test_create_pbk():
    kdf = credentials().create_pbk()
    
def test_image_encryption():
    images_path = os.listdir(os.path.join(os.getcwd(),"known_users"))

    faces = []
    
    allowed_files = ["png","jpg","jpeg","gif"]

    for image in images_path:
        file = f"{image}".split(".")
        if file[1] not in allowed_files:
            continue
        faces.append(image)
        
    for face in faces:
        image_path = os.path.join(os.getcwd(),f"known_users/{face}")
        
        print(image_path)
        with open(image_path, "rb") as face:
            original_image = face.read()
        
        keys = credentials().generate_keys()
        
        fernet = encryption().gen_multi_fernet(keys)
        
        image_hash = encryption().get_image_hash(original_image)
        
        encrypted_image = encryption().encrypt_image(fernet=fernet,image=original_image)
        
        encrypted_image_hash = encryption().get_image_hash(encrypted_image)
        
        print(encryption().compare_image_hash(original_image,encrypted_image))
        
        decrypted_image = encryption().decrypt_image(fernet=fernet,encrypted_image=encrypted_image)
        
        print(encryption().compare_image_hash(original_image,decrypted_image))
        