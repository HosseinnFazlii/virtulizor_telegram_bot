from cryptography.fernet import Fernet
import hashlib
import base64

custom_key = '0ba1)h=nz&td-by)@9-otkatza3md!w_f=0)(ph65#&q=@@@qa'


hashed_key = hashlib.sha256(custom_key.encode()).digest()


fernet_key = base64.urlsafe_b64encode(hashed_key[:32])


f = Fernet(fernet_key)

def decrypt_id(encrypted_id):
    return f.decrypt(encrypted_id).decode()

encrypted_id = b'gAAAAABmxZ9VOU7hGsIVn5pu8g_DffUO3-GRoMCKMrF7CTG38oDI3xS8CcZu3Ym6NU6dekYskT_28c_HH7JHHyK1vl4P9EWrVA=='


encyptioncryptogeraphy = decrypt_id(encrypted_id)
print(encyptioncryptogeraphy)
