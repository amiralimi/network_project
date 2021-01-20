from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
import base64, os


def generate_keys():
    modulus_length = 4096
    private_key = RSA.generate(modulus_length, Random.new().read)
    public_key = private_key.publickey()
    return private_key, public_key


def encrypt_message(message, public_key):
    encrypted_msg = public_key.encrypt(message, 64)[0]
    encoded_encrypted_msg = base64.b64encode(encrypted_msg)  # base64 encoded strings are database friendly
    return encoded_encrypted_msg


def decrypt_message(encrypted_msg, private_key):
    decoded_msg = base64.b64decode(encrypted_msg)
    decoded_decrypted_msg = private_key.decrypt(decoded_msg)
    return decoded_decrypted_msg


def generate_secret_key_for_AES_cipher():
    AES_key_length = 32
    secret_key = os.urandom(AES_key_length)
    encoded_secret_key = base64.b64encode(secret_key)
    return encoded_secret_key


def encrypt_message_AES(private_msg, encoded_secret_key, padding_character):
    secret_key = base64.b64decode(encoded_secret_key)
    cipher = AES.new(secret_key)
    padded_private_msg = private_msg + (padding_character * ((16 - len(private_msg)) % 16))
    encrypted_msg = cipher.encrypt(padded_private_msg)
    encoded_encrypted_msg = base64.b64encode(encrypted_msg)
    return encoded_encrypted_msg


def decrypt_message_AES(encoded_encrypted_msg, encoded_secret_key, padding_character):
    secret_key = base64.b64decode(encoded_secret_key)
    encrypted_msg = base64.b64decode(encoded_encrypted_msg)
    cipher = AES.new(secret_key)
    decrypted_msg = cipher.decrypt(encrypted_msg)
    unpadded_private_msg = decrypted_msg.rstrip(padding_character)
    return unpadded_private_msg
