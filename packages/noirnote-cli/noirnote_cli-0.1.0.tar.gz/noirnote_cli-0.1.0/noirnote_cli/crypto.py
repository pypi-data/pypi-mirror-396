# noirnote-cli/noirnote_cli/crypto.py
import base64
import hmac
import hashlib
import traceback
from typing import Tuple

from Crypto.Cipher import AES

# Imports from cryptography library as required by the spec
from cryptography.exceptions import InvalidTag, InvalidSignature
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def create_request_signature(secret_key: str, message: str) -> str:
    """
    Creates an HMAC-SHA256 signature for a given message.
    """
    try:
        key_bytes = secret_key.encode('utf-8')
        message_bytes = message.encode('utf-8')

        signature = hmac.new(key_bytes, message_bytes, hashlib.sha256).hexdigest()
        return signature
    except Exception as e:
        print(f"FATAL: Could not generate request signature: {e}")
        raise

def decrypt_secret(secret_key_bytes: bytes, encrypted_data_b64: str, tag_b64: str) -> str:
    """
    Decrypts a payload using AES-256-GCM, matching the main application's logic.
    """
    try:
        encrypted_data_bytes = base64.b64decode(encrypted_data_b64)
        tag_bytes = base64.b64decode(tag_b64)

        nonce_size = 16  # As per pycryptodome's AES.MODE_GCM default
        if len(encrypted_data_bytes) < nonce_size:
            raise ValueError("Invalid encrypted data: too short to contain a nonce.")

        nonce = encrypted_data_bytes[:nonce_size]
        ciphertext = encrypted_data_bytes[nonce_size:]

        cipher = AES.new(secret_key_bytes, AES.MODE_GCM, nonce=nonce)
        plaintext_bytes = cipher.decrypt_and_verify(ciphertext, tag_bytes)

        return plaintext_bytes.decode("utf-8")

    except (ValueError, KeyError) as e:
        print(f"Decryption failed: {e}")
        raise ValueError("Decryption failed. The secret key may be incorrect or the data is corrupted.") from e
    except Exception as e:
        print(f"An unexpected error occurred during decryption: {e}")
        traceback.print_exc()
        raise

# --- NEW FUNCTIONS as per specification ---

def decrypt_private_key_with_master_key(master_key_bytes: bytes, encrypted_key_payload_b64: str) -> str:
    """
    Decrypts the user's asymmetric private key using their personal master key (AES-GCM).
    """
    try:
        encrypted_payload = base64.b64decode(encrypted_key_payload_b64)
        # Assumes 12-byte nonce, which is standard for GCM when not managed externally.
        nonce = encrypted_payload[:12]
        # The rest of the payload is ciphertext + tag
        ciphertext_with_tag = encrypted_payload[12:]
        aesgcm = AESGCM(master_key_bytes)
        decrypted_pem_bytes = aesgcm.decrypt(nonce, ciphertext_with_tag, None)
        return decrypted_pem_bytes.decode('utf-8')
    except InvalidTag:
        raise ValueError("Decryption of private key failed. The Master Recovery Key may be incorrect or the data is corrupted.")
    except Exception as e:
        raise RuntimeError(f"An unexpected low-level error occurred during private key decryption: {e}")

# --- COPIED FUNCTIONS from app/crypto_utils.py ---

def decrypt_with_private_key(private_key, encrypted_data: bytes) -> bytes:
    """Decrypts data using an RSA private key with OAEP padding."""
    decrypted_data = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_data

def deserialize_pem_to_key(pem_bytes: bytes, is_private=False) -> any:
    """Deserializes a PEM-encoded key into a key object."""
    if is_private:
        return serialization.load_pem_private_key(pem_bytes, password=None)
    else:
        return serialization.load_pem_public_key(pem_bytes)