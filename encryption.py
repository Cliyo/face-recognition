import base64
from cryptography.fernet import Fernet, MultiFernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from string import ascii_letters, digits
from secrets import choice
from os import urandom

class credentials:
    def __init__(self) -> None:
        self.SPECIAL_CHARACTERS = "!#*$%&"
        
        self.KEY_LENGTH= 16
        
        self.randomize = 16
        
    def generate_keys(self, key_number = 3) -> str:
        keys = []
        
        for i in range(key_number):
            unencrypted_key = self.gen_decrypted_key()
            
            kdf = self.create_pbk()
            
            key = base64.urlsafe_b64encode(kdf.derive(unencrypted_key)).decode('utf-8')
            
            keys.append(key)
        
        return keys
    
    def gen_decrypted_key(self) -> bytes:
        valid_characters = ascii_letters + digits + self.SPECIAL_CHARACTERS
        unencrypted_key = b''.join(choice(valid_characters).encode() for _ in range(self.KEY_LENGTH))
        return unencrypted_key
    
    def create_pbk(self) -> PBKDF2HMAC:
        salt = urandom(self.randomize)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        
        return kdf

class encryption:
    def __init__(self) -> None:
        pass
    
    def gen_multi_fernet(self,keys: list) -> MultiFernet:
        fernet_keys = [Fernet(key.encode("utf-8")) for key in keys]
        
        fernet = MultiFernet(fernet_keys)
        
        return fernet
    
    def encrypt_image(self,fernet: MultiFernet, image: bytes):
        encrypted_image = fernet.encrypt(image)
        
        return encrypted_image
    
    def decrypt_image(self,fernet: MultiFernet, encrypted_image: bytes):
        decrypted_image = fernet.decrypt(encrypted_image)
        
        return decrypted_image
        
    def get_image_hash(self,image: bytes) -> str:
        sha = hashes.Hash(hashes.SHA256(), backend=default_backend())
        
        sha.update(image)
        
        hash = sha.finalize()
        
        return hash.hex()
    
    def compare_image_hash(self,image1: bytes, image2: bytes) -> bool:
        hash1 = self.get_image_hash(image1)
        hash2 = self.get_image_hash(image2)
        
        return hash1 == hash2
    
    def compare_hash(self,hash1: str, hash2: str) -> bool:
        return hash1 == hash2
    
    # def keys_base64(self,keys: list):
    #     return [key.decode("utf-8") for key in keys]
    
    # def encode_keys(self,keys_base64: list):
    #     return [key.encode("utf-8") for key in keys_base64]