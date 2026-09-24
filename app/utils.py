from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

print("recommended hasher = ", password_hash.current_hasher)

def hash(password:str):
    return password_hash.hash(password)