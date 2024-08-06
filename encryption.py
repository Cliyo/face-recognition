import base64
from cryptography.fernet import Fernet, MultiFernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from string import ascii_letters, digits
from secrets import choice
from os import urandom

class credentials:
    def __init__(self) -> None:
        self.SPECIAL_CHARACTERS = "!#*$%&"
        
        self.KEY_LENGTH= 16
        
        self.randomize = 16
        
    def generate_token(self, key_number = 3) -> str:
        keys = []
        
        for i in range(key_number):
            unencrypted_key = self.generate_key()
            
            kdf = self.create_pbk()
            
            key = base64.urlsafe_b64encode(kdf.derive(unencrypted_key))
            
            keys.append(key)
        
        fernet = MultiFernet(keys)
        
        return fernet
    
    def generate_key(self) -> bytes:
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

if __name__ == "__main__":
    print(credentials().generate_token())