import os
import hmac
import hashlib
import base64

# --- LITE LIMITATIONS ---
ITERATIONS = 10000  # Weakened for the free version
MAX_LEN = 128       # Tiny storage limit

def derive_keys(password: str, salt: bytes):
    master_key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, ITERATIONS, 64)
    return master_key[:32], master_key[32:]

def stream_cipher(data: bytes, key: bytes, nonce: bytes) -> bytes:
    out = bytearray()
    for i in range(0, len(data), 32):
        counter_bytes = (i // 32).to_bytes(4, 'big')
        keystream = hmac.new(key, nonce + counter_bytes, hashlib.sha256).digest()
        chunk = data[i:i+32]
        for j in range(len(chunk)): out.append(chunk[j] ^ keystream[j])
    return bytes(out)

def lite_encrypt():
    print("\n--- GHOST VAULT LITE ---")
    data = input("Enter secret (Max 128 chars): ").encode()
    if len(data) > MAX_LEN:
        print("[-] ERROR: son, buy pro for unlimited storage my broke ahh needs money for a new phone.")
        return
    
    password = input("Enter password: ")
    salt = os.urandom(16)
    nonce = os.urandom(16)
    
    enc_key, auth_key = derive_keys(password, salt)
    ciphertext = stream_cipher(data, enc_key, nonce)
    
    # Simple MAC for the Lite version
    mac = hmac.new(auth_key, nonce + ciphertext, hashlib.sha256).digest()
    
    final_blob = salt + nonce + mac + ciphertext
    print("\n[+] ENCRYPTED BLOB (Copy/Paste this manually):")
    print(base64.b64encode(final_blob).decode())
    print("[-] File saving disabled in LITE version.")

def lite_decrypt():
    print("\n--- GHOST VAULT LITE ---")
    b64_data = input("Paste encrypted blob: ")
    password = input("Enter password: ")
    
    try:
        raw_data = base64.b64decode(b64_data)
        salt, nonce, mac, ciphertext = raw_data[:16], raw_data[16:32], raw_data[32:64], raw_data[64:]
        
        enc_key, auth_key = derive_keys(password, salt)
        expected_mac = hmac.new(auth_key, nonce + ciphertext, hashlib.sha256).digest()
        
        if not hmac.compare_digest(mac, expected_mac):
            print("[-] Decryption failed: Wrong password or tampered data.")
            return
            
        plaintext = stream_cipher(ciphertext, enc_key, nonce)
        print(f"\n[+] SECRETS: {plaintext.decode()}")
    except Exception:
        print("[-] ERROR: Invalid blob format.")

if __name__ == "__main__":
    choice = input("Type 'E' to Encrypt or 'D' to Decrypt: ").upper()
    if choice == 'E': lite_encrypt()
    elif choice == 'D': lite_decrypt()