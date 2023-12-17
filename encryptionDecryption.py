from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode


def encrypt_text(text, key):
    try:
        # Ensure the key is 8 bytes long
        key = key[:8].encode('utf-8')

        # Generate a random IV (Initialization Vector)
        iv = get_random_bytes(8)

        # Create a DES cipher object
        cipher = DES.new(key, DES.MODE_CBC, iv)

        # Pad the plaintext and encrypt it
        padded_data = pad(text.encode('utf-8'), DES.block_size)
        ciphertext = cipher.encrypt(padded_data)

        # Combine the IV and ciphertext
        encrypted_data = iv + ciphertext

        # Base64 encode the result for easier storage and transmission
        return b64encode(encrypted_data).decode('utf-8')
    except:
        return "Invalid"


def decrypt_text(encrypted_text, key):
    try:
        # if the encrypted text is empty return empty string
        if encrypted_text == "":
            return ""

        # if their is problem with the key return empty string
        if len(key) < 8:
            return ""

        # Ensure the key is 8 bytes long
        key = key[:8].encode('utf-8')

        # Base64 decode the encrypted data
        encrypted_data = b64decode(encrypted_text.encode('utf-8'))

        # Extract the IV from the encrypted data
        iv = encrypted_data[:8]

        # Create a DES cipher object
        cipher = DES.new(key, DES.MODE_CBC, iv)

        # Decrypt the data and remove padding
        decrypted_data = unpad(cipher.decrypt(
            encrypted_data[8:]), DES.block_size)

        return decrypted_data.decode('utf-8')
    except:
        return "Invalid"
