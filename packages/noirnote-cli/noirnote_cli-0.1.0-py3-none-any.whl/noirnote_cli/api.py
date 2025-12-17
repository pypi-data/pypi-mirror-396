# noirnote-cli/noirnote_cli/api.py
import requests
import json
from typing import Tuple, Dict, Any, Optional
import sys

from . import auth

# This base URL is for 1st Gen functions. 2nd Gen functions will use their own full URL.
NOIRNOTE_API_BASE_URL = "https://europe-west3-noirnote.cloudfunctions.net"

class NoirNoteAPIClient:
    """A client for making direct HTTPS requests to the NoirNote API."""

    def __init__(self):
        self.api_key_endpoint = f"{NOIRNOTE_API_BASE_URL}/getEncryptedSecretPayload"
        self.session = requests.Session()

    def _get_headers_with_app_check(self, id_token: str) -> Dict[str, str]:
        headers = {"Authorization": f"Bearer {id_token}", "Content-Type": "application/json"}
        try:
            # This call itself prints, we will silence it in auth.py
            app_check_token = auth.get_cli_app_check_token(id_token)
            if app_check_token:
                headers["X-Firebase-AppCheck"] = app_check_token
        except Exception as e:
            # Silenced this warning
            pass
        return headers

    def _handle_api_error(self, e: requests.exceptions.HTTPError):
        """Centralized error handler for API calls."""
        error_details = e.response.text
        try:
            json_error = e.response.json().get('error', {})
            message = json_error.get('message', error_details)
            status = json_error.get('status', e.response.status_code)
            raise Exception(f"API Error ({status}): {message}") from e
        except (json.JSONDecodeError, AttributeError):
            raise Exception(f"API Error ({e.response.status_code}): {error_details}") from e
    
    def _create_data_payload(self, base_payload: dict, team_id: str | None) -> dict:
        """Helper to create the final JSON payload for a callable function."""
        if team_id:
            base_payload["teamId"] = team_id
        return {"data": base_payload}

    # --- AUTH & CONFIGURATION METHODS ---
    def get_firebase_cli_config(self, id_token: str) -> Dict[str, Any]:
        """
        Fetches the public Firebase configuration from a secure cloud function.
        Requires a valid user ID token and App Check token.
        """
        endpoint = "https://getfirebasecliconfig-j7shkcz2nq-ey.a.run.app/getFirebaseCliConfig"
        payload = {"data": {}}
        headers = self._get_headers_with_app_check(id_token)
        try:
            response = self.session.post(endpoint, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            result = response.json().get('result')
            if not result or not isinstance(result, dict):
                raise KeyError("API response missing 'result' dictionary or is not a valid config.")
            return result
        except requests.exceptions.HTTPError as e:
            self._handle_api_error(e)
        except Exception as e:
            raise Exception(f"Failed to fetch Firebase CLI config: {e}") from e

    def get_user_auth_details(self, email: str) -> Dict[str, Any]:
        """Fetches public auth details (salt, etc.). This is an unauthenticated endpoint."""
        endpoint = f"{NOIRNOTE_API_BASE_URL}/getUserAuthDetails"
        try:
            response = self.session.post(endpoint, json={"email": email.lower()}, headers={"Content-Type": "application/json"}, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404: raise Exception(f"User with email '{email}' not found.")
            else: self._handle_api_error(e)
        except Exception as e:
            raise Exception(f"An unexpected error occurred during auth details API call: {e}") from e

    def get_user_public_auth_data(self, id_token: str) -> Dict[str, Any]:
        """Fetches the user's encrypted asymmetric private key."""
        endpoint = f"{NOIRNOTE_API_BASE_URL}/getUserPublicAuthData"
        payload = {"data": {}}
        headers = self._get_headers_with_app_check(id_token)
        try:
            response = self.session.post(endpoint, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            result = response.json().get('result')
            if not result or 'encrypted_private_key_A' not in result:
                raise KeyError("API response missing 'result.encrypted_private_key_A'.")
            return result
        except requests.exceptions.HTTPError as e: self._handle_api_error(e)
        except Exception as e: raise Exception(f"Failed to fetch user public auth data: {e}") from e

    def list_user_teams(self, id_token: str) -> list:
        """Fetches the user's teams and their metadata."""
        endpoint = f"{NOIRNOTE_API_BASE_URL}/listUserTeams"
        payload = {"data": {}}
        headers = self._get_headers_with_app_check(id_token)
        try:
            response = self.session.post(endpoint, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            result = response.json().get('result')
            if not result or 'teams' not in result:
                raise KeyError("API response missing 'result.teams'.")
            return result['teams']
        except requests.exceptions.HTTPError as e: self._handle_api_error(e)
        except Exception as e: raise Exception(f"Failed to list user teams: {e}") from e

    # --- WORKSPACE-AWARE DATA METHODS ---
    def list_jobs(self, id_token: str, team_id: Optional[str] = None) -> list:
        endpoint = f"{NOIRNOTE_API_BASE_URL}/listJobs"
        payload = self._create_data_payload({}, team_id)
        headers = self._get_headers_with_app_check(id_token)
        try:
            response = self.session.post(endpoint, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json().get('result', {}).get('jobs', [])
        except requests.exceptions.HTTPError as e: self._handle_api_error(e)
        except Exception as e: raise Exception(f"Failed to fetch job history: {e}") from e

    def get_note_payload(self, id_token: str, note_id: str, team_id: Optional[str] = None) -> Dict[str, str]:
        endpoint = f"{NOIRNOTE_API_BASE_URL}/getNotePayload"
        payload = self._create_data_payload({"noteId": note_id}, team_id)
        headers = self._get_headers_with_app_check(id_token)
        try:
            response = self.session.post(endpoint, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            result = response.json().get('result')
            if not result: raise KeyError("API response missing 'result' key.")
            return result
        except requests.exceptions.HTTPError as e: self._handle_api_error(e)
        except Exception as e: raise Exception(f"Failed to fetch note payload: {e}") from e

    def find_note_by_name(self, id_token: str, search_term: str, team_id: Optional[str] = None) -> list:
        endpoint = f"{NOIRNOTE_API_BASE_URL}/findNoteByName"
        payload = self._create_data_payload({"searchTerm": search_term}, team_id)
        headers = self._get_headers_with_app_check(id_token)
        try:
            response = self.session.post(endpoint, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json().get('result', {}).get('matches', [])
        except requests.exceptions.HTTPError as e: self._handle_api_error(e)
        except Exception as e: raise Exception(f"Failed to search for note: {e}") from e

    def get_vault_secret_payload(self, id_token: str, secret_id: str, team_id: Optional[str] = None) -> dict:
        endpoint = f"{NOIRNOTE_API_BASE_URL}/getVaultSecretPayload"
        payload = self._create_data_payload({"secretId": secret_id}, team_id)
        headers = self._get_headers_with_app_check(id_token)
        try:
            response = self.session.post(endpoint, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            result = response.json().get('result')
            if not result: raise KeyError("API response missing 'result' key.")
            return result
        except requests.exceptions.HTTPError as e: self._handle_api_error(e)
        except Exception as e: raise Exception(f"Failed to fetch secret payload: {e}") from e

    def get_secret_index(self, id_token: str, team_id: Optional[str] = None) -> list:
        endpoint = f"{NOIRNOTE_API_BASE_URL}/getSecretIndex"
        payload = self._create_data_payload({}, team_id)
        headers = self._get_headers_with_app_check(id_token)
        try:
            response = self.session.post(endpoint, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json().get('result', {}).get('secret_index', [])
        except requests.exceptions.HTTPError as e: self._handle_api_error(e)
        except Exception as e: raise Exception(f"Failed to fetch secret index: {e}") from e

    def list_notes(self, id_token: str, team_id: Optional[str] = None) -> list:
        """Fetches the note library index (ID and name) for the active workspace."""
        endpoint = f"{NOIRNOTE_API_BASE_URL}/listNotes"
        payload = self._create_data_payload({}, team_id)
        headers = self._get_headers_with_app_check(id_token)
        try:
            response = self.session.post(endpoint, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json().get('result', {}).get('notes', [])
        except requests.exceptions.HTTPError as e:
            self._handle_api_error(e)
        except Exception as e:
            raise Exception(f"Failed to fetch note library: {e}") from e

    def get_script_library_index(self, id_token: str, team_id: Optional[str] = None) -> list:
        endpoint = f"{NOIRNOTE_API_BASE_URL}/getScriptLibraryIndex"
        payload = self._create_data_payload({}, team_id)
        headers = self._get_headers_with_app_check(id_token)
        try:
            response = self.session.post(endpoint, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json().get('result', {}).get('scripts', [])
        except requests.exceptions.HTTPError as e: self._handle_api_error(e)
        except Exception as e: raise Exception(f"Failed to fetch script library: {e}") from e

    def get_script_payload(self, id_token: str, script_id: str, team_id: Optional[str] = None) -> Dict[str, str]:
        endpoint = f"{NOIRNOTE_API_BASE_URL}/getScriptPayload"
        payload = self._create_data_payload({"scriptId": script_id}, team_id)
        headers = self._get_headers_with_app_check(id_token)
        try:
            response = self.session.post(endpoint, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            result = response.json().get('result')
            if not result: raise KeyError("API response missing 'result' key.")
            return result
        except requests.exceptions.HTTPError as e: self._handle_api_error(e)
        except Exception as e: raise Exception(f"An unexpected error occurred while fetching script payload: {e}") from e
    
    # --- LEGACY CI/CD METHOD (unchanged logic) ---
    def get_encrypted_payload(self, api_key: str) -> Tuple[str, str]:
        payload = {"apiKey": api_key}
        headers = {"Content-Type": "application/json"}
        try:
            response = self.session.post(self.api_key_endpoint, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            result = response.json()
            encrypted_value = result.get('re_encrypted_value_b64')
            tag = result.get('tag_b64')
            if not encrypted_value or not tag:
                raise KeyError("API response for API key secret was successful but is missing required data.")
            return encrypted_value, tag
        except requests.exceptions.HTTPError as e:
            raise Exception(f"API Error ({e.response.status_code}) fetching API key secret: {e.response.text}") from e
        except Exception as e:
            raise Exception(f"An unexpected error occurred during API key secret API call: {e}") from e