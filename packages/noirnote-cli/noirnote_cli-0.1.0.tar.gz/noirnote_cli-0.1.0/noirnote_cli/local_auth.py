# noirnote-cli/noirnote_cli/local_auth.py
import os
import json
import base64
import hashlib
from pathlib import Path
from typing import Dict, Any

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

# --- Core Logic Adapted from app/utils.py ---

def _get_user_settings_path(email: str) -> Path:
    """Helper function to get the path for a user's local settings file."""
    email_filename = email.lower() + "_settings.json"
    settings_dir = Path.home() / ".noirnote"
    return settings_dir / email_filename

def load_user_data(email: str) -> Dict[str, Any] | None:
    """
    Loads user-specific data from the local settings file.
    Returns the data as a dictionary, or None if the file doesn't exist.
    """
    user_settings_file = _get_user_settings_path(email)
    if not user_settings_file.exists():
        return None
    try:
        return json.loads(user_settings_file.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, IOError) as e:
        # In a CLI context, we can raise this as a critical error.
        raise RuntimeError(f"Local user data file for {email} is corrupted: {e}") from e

def _derive_key(password: str, salt: bytes) -> bytes:
    """Derives a 32-byte key from a password and salt using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return kdf.derive(password.encode('utf-8'))

def decrypt_private_key_from_local_data(user_data: dict, password: str) -> str:
    """
    Decrypts the user's asymmetric private key from local data using their password.
    This is for Scenario A (Normal Login).
    """
    try:
        salt_b64 = user_data['salt_b64']
        encrypted_key_payload_b64 = user_data['encrypted_private_key_B']
        salt = base64.b64decode(salt_b64)
        encrypted_payload = base64.b64decode(encrypted_key_payload_b64)
        derived_key = _derive_key(password, salt)
        nonce, ciphertext = encrypted_payload[:12], encrypted_payload[12:]
        aesgcm = AESGCM(derived_key)
        decrypted_private_key_pem_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted_private_key_pem_bytes.decode('utf-8')
    except InvalidTag:
        raise ValueError("Invalid password.")
    except Exception as e:
        raise RuntimeError(f"Failed to decrypt local private key: {e}")

def derive_master_key_from_private_key(private_key_pem: str) -> bytes:
    """
    Deterministically derives the 32-byte personal master key from the private key PEM string.
    """
    return hashlib.sha256(private_key_pem.encode('utf-8')).digest()

def save_local_user_file(email: str, password: str, user_id: str, private_key_pem: str):
    """
    Creates the local user settings file on a new device. Re-encrypts the
    private key with the current password for local storage (Key B).
    """
    user_settings_file = _get_user_settings_path(email)
    settings_dir = user_settings_file.parent
    settings_dir.mkdir(parents=True, exist_ok=True)

    # 1. Create a new salt for local encryption.
    salt = os.urandom(16)
    derived_password_key = _derive_key(password, salt)
    
    # 2. Encrypt the provided private key PEM.
    aesgcm_local = AESGCM(derived_password_key)
    nonce_b = os.urandom(12)
    encrypted_private_key_B = aesgcm_local.encrypt(nonce_b, private_key_pem.encode('utf-8'), None)
    encrypted_payload_B = nonce_b + encrypted_private_key_B

    # 3. Assemble and save the local data file.
    local_data = {
        "email": email.lower(),
        "user_id": user_id,
        "salt_b64": base64.b64encode(salt).decode('utf-8'),
        "encrypted_private_key_B": base64.b64encode(encrypted_payload_B).decode('utf-8'),
    }

    user_settings_file.write_text(json.dumps(local_data, indent=4), encoding='utf-8')