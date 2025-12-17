# noirnote_cli/keychain.py
import keyring
import keyring.errors
import platform
import sys
import os

# Define a unique service name for your application.
SERVICE_NAME = "app.noirnote.cli"

def _is_wsl() -> bool:
    if 'microsoft-standard' in platform.uname().release.lower(): return True
    if os.path.exists('/proc/version') and 'microsoft' in open('/proc/version').read().lower(): return True
    return False

def _initialize_keyring_backend():
    try:
        default_keyring = keyring.get_keyring()
        from keyring.backends.fail import Keyring as FailKeyring
        from keyring.backends.null import Keyring as NullKeyring
        is_unusable_backend = isinstance(default_keyring, (FailKeyring, NullKeyring))
        if (_is_wsl() and 'SecretService' in type(default_keyring).__name__) or is_unusable_backend:
            from keyrings.cryptfile.cryptfile import EncryptedKeyring
            kr = EncryptedKeyring()
            _ = kr.priority
            keyring.set_keyring(kr)
    except keyring.errors.NoKeyringError:
        raise RuntimeError("No secure credential storage available on this system.")
    except Exception as e:
        raise RuntimeError(f"Could not initialize secure credential storage: {e}")

_initialize_keyring_backend()

def store_keys(user_email: str, master_key_b64: str, private_key_pem: str) -> None:
    """
    Stores the user's master key and private key securely in the OS keychain.
    """
    if not all([user_email, master_key_b64, private_key_pem]):
        raise ValueError("User email, master key, and private key PEM cannot be empty.")
    try:
        username_master = user_email.lower()
        username_private = f"{user_email.lower()}_private_key"
        print(f"--> Keychain: Storing master key for user '{username_master}'...")
        keyring.set_password(SERVICE_NAME, username_master, master_key_b64)
        print(f"--> Keychain: Storing private key for user '{username_private}'...")
        keyring.set_password(SERVICE_NAME, username_private, private_key_pem)
        print("--> Keychain: Keys stored successfully.")
    except Exception as e:
        print(f"CRITICAL: Failed to store keys in keychain: {e}", file=sys.stderr)
        raise RuntimeError(f"Could not save keys to the OS keychain: {e}")

def get_keys(user_email: str) -> tuple[str, str] | None:
    """
    Retrieves the user's master key and private key from the OS keychain.
    Returns a tuple (master_key_b64, private_key_pem) or None if not all keys are found.
    """
    if not user_email:
        return None
    try:
        username_master = user_email.lower()
        username_private = f"{user_email.lower()}_private_key"
        master_key = keyring.get_password(SERVICE_NAME, username_master)
        private_key = keyring.get_password(SERVICE_NAME, username_private)
        if master_key and private_key:
            return master_key, private_key
        return None
    except Exception as e:
        print(f"CRITICAL: Failed to retrieve keys from keychain: {e}", file=sys.stderr)
        raise RuntimeError(f"Could not retrieve keys from the OS keychain: {e}")

def delete_keys(user_email: str) -> None:
    """
    Deletes the user's master and private keys from the OS keychain.
    """
    if not user_email:
        return
    try:
        username_master = user_email.lower()
        username_private = f"{user_email.lower()}_private_key"
        print(f"--> Keychain: Deleting keys for user '{user_email}'...")
        # Check before deleting to avoid errors if a key is already gone
        if keyring.get_password(SERVICE_NAME, username_master) is not None:
            keyring.delete_password(SERVICE_NAME, username_master)
        if keyring.get_password(SERVICE_NAME, username_private) is not None:
            keyring.delete_password(SERVICE_NAME, username_private)
        print("--> Keychain: Keys deleted successfully.")
    except Exception as e:
        print(f"CRITICAL: Failed to delete keys from keychain: {e}", file=sys.stderr)
        raise RuntimeError(f"Could not delete keys from the OS keychain: {e}")

def get_active_user() -> str | None:
    config_dir = os.path.join(os.path.expanduser("~"), ".config", "noirnote-cli")
    active_user_file = os.path.join(config_dir, "active_user.txt")
    if os.path.exists(active_user_file):
        with open(active_user_file, 'r') as f:
            return f.read().strip()
    return None

def set_active_user(user_email: str) -> None:
    config_dir = os.path.join(os.path.expanduser("~"), ".config", "noirnote-cli")
    os.makedirs(config_dir, exist_ok=True)
    active_user_file = os.path.join(config_dir, "active_user.txt")
    with open(active_user_file, 'w') as f:
        f.write(user_email.lower())

def clear_active_user() -> None:
    config_dir = os.path.join(os.path.expanduser("~"), ".config", "noirnote-cli")
    active_user_file = os.path.join(config_dir, "active_user.txt")
    if os.path.exists(active_user_file):
        os.remove(active_user_file)