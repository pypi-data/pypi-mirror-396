# noirnote_cli/noirnote_cli/auth.py
import pyrebase
import json
import os
from pathlib import Path
import requests
import traceback
import sys
from typing import Dict, Any, Optional, Tuple

# --- Path definitions for storing credentials and config ---
CONFIG_DIR = Path.home() / ".config" / "noirnote-cli"
CREDS_FILE = CONFIG_DIR / "creds.json"
API_CREDS_FILE = CONFIG_DIR / "api_creds.json"  # New path for API keys
FIREBASE_CONFIG_FILE = CONFIG_DIR / "firebase_config.json"

# --- Firebase Client Initialization ---
def _get_firebase_client():
    """Initializes and returns the Pyrebase4 client from a stored config file."""
    if not FIREBASE_CONFIG_FILE.exists():
        raise FileNotFoundError(
            "Firebase config not found. Please run 'noirnote-cli login' to create it."
        )
    with open(FIREBASE_CONFIG_FILE, 'r') as f:
        config = json.load(f)
    return pyrebase.initialize_app(config)

def get_current_id_token() -> Optional[str]:
    """
    Gets the current ID token from the local creds file, refreshing it if it's expired.

    Returns:
        A valid ID token string, or None if authentication fails.
    """
    if not CREDS_FILE.exists():
        # This is expected if using API key auth, so we don't print an error here.
        return None

    try:
        with open(CREDS_FILE, 'r') as f:
            creds = json.load(f)
    except (json.JSONDecodeError, Exception):
        # Fail silently, let the calling function handle the None token.
        return None

    refresh_token = creds.get("refreshToken")
    if not refresh_token:
        clear_firebase_creds()
        return None

    try:
        firebase = _get_firebase_client()
        auth_client = firebase.auth()
        user = auth_client.refresh(refresh_token)
        creds["idToken"] = user.get('idToken')
        creds["refreshToken"] = user.get('refreshToken')
        with open(CREDS_FILE, 'w') as f:
            json.dump(creds, f)
        return user.get('idToken')
    except Exception:
        clear_firebase_creds()
        return None

def store_firebase_creds(email: str, creds: dict, firebase_config: dict):
    """Saves user credentials (idToken, refreshToken) and the public firebase config locally."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CREDS_FILE, 'w') as f:
        json.dump(creds, f)
    with open(FIREBASE_CONFIG_FILE, 'w') as f:
        json.dump(firebase_config, f)

def clear_firebase_creds():
    """Removes all local credential and firebase config files upon logout."""
    try:
        # Clear interactive user creds
        if CREDS_FILE.exists(): os.remove(CREDS_FILE)
        if FIREBASE_CONFIG_FILE.exists(): os.remove(FIREBASE_CONFIG_FILE)
        # Clear API key creds
        if API_CREDS_FILE.exists(): os.remove(API_CREDS_FILE)
    except OSError as e:
        print(f"--> auth: Error clearing local credential files: {e}", file=sys.stderr)

# --- New Functions for API Key Authentication ---

def store_api_credentials(api_key: str, api_secret: str):
    """Saves API Key ID and Secret Access Key to a dedicated file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    credentials = {
        "api_key_id": api_key,
        "secret_access_key": api_secret
    }
    with open(API_CREDS_FILE, 'w') as f:
        json.dump(credentials, f)

def get_api_credentials() -> Optional[Tuple[str, str]]:
    """
    Reads API credentials from the dedicated file.
    Returns (api_key_id, secret_access_key) or None if not found.
    """
    if not API_CREDS_FILE.exists():
        return None
    try:
        with open(API_CREDS_FILE, 'r') as f:
            creds = json.load(f)
            key_id = creds.get("api_key_id")
            secret_key = creds.get("secret_access_key")
            if key_id and secret_key:
                return key_id, secret_key
            return None
    except (json.JSONDecodeError, IOError):
        return None


def get_cli_app_check_token(id_token: str) -> Optional[str]:
    """
    Fetches a new App Check token for the CLI by calling the
    getCustomAppCheckToken Cloud Function.
    """
    if not FIREBASE_CONFIG_FILE.exists(): return None
    try:
        with open(FIREBASE_CONFIG_FILE, 'r') as f:
            firebase_config = json.load(f)
    except Exception as e:
        return None

    app_id = firebase_config.get("appId")
    project_id = firebase_config.get("projectId")
    if not app_id or not project_id: return None

    cloud_function_base_url = f"https://europe-west3-{project_id}.cloudfunctions.net"
    app_check_endpoint = f"{cloud_function_base_url}/getCustomAppCheckToken"

    payload = {"data": {"appId": app_id}}
    headers = {"Authorization": f"Bearer {id_token}", "Content-Type": "application/json"}
    
    try:
        response = requests.post(app_check_endpoint, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        response_data = response.json()
        result = response_data.get('result')
        if not result: return None
        app_check_token = result.get("token")
        if not app_check_token: return None
        return app_check_token
    except requests.exceptions.RequestException:
        return None