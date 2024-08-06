from encryption import credentials

def test_generate_keys():
    key = credentials().generate_key()
    key2 = credentials().generate_key()
    
def test_generate_token():
    fernet = credentials().generate_token()
    
def test_create_pbk():
    kdf = credentials().create_pbk()