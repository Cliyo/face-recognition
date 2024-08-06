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
        
    def generate_token(self) -> str:
        unencrypted_key1 = self.generate_key()
        unencrypted_key2 = self.generate_key()
        unencrypted_key3 = self.generate_key()
        
        kdf1 = self.create_pbk()
        kdf2 = self.create_pbk()
        kdf3 = self.create_pbk()
        
        key1 = base64.urlsafe_b64encode(kdf1.derive(unencrypted_key1))
        key2 = base64.urlsafe_b64encode(kdf2.derive(unencrypted_key2))
        key3 = base64.urlsafe_b64encode(kdf3.derive(unencrypted_key3))
        
        fernet = MultiFernet([key1,key2,key3])
        
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