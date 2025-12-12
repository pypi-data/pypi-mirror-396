import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def decrypt(encrypted_text: str, key_string: str) -> str:
    key_bytes = key_string.encode("utf-8")

    # Create AES cipher object
    cipher = AES.new(key_bytes, AES.MODE_ECB)

    # Decode Base64 and decrypt
    encrypted_bytes = base64.b64decode(encrypted_text)
    decrypted_bytes = cipher.decrypt(encrypted_bytes)

    # Unpad and decode
    decrypted_text = unpad(decrypted_bytes, AES.block_size).decode("utf-8")
    return decrypted_text
