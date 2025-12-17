# noirnote-cli/noirnote_cli/main.py

import os
import sys
import subprocess
import click
import base64
import json
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import traceback
import requests
import warnings
import questionary
from questionary import Choice

# --- Rich TUI Library Imports ---
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

# --- Suppress the pkg_resources warning from gcloud/pyrebase4 ---
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=UserWarning, module='gcloud')
    from .api import NoirNoteAPIClient
    from . import auth
    import pyrebase

# Local application imports
from . import crypto
from . import keychain
from . import local_auth

# Cryptography imports
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# --- STATE MANAGEMENT & HELPERS ---
CONFIG_DIR = Path.home() / ".config" / "noirnote-cli"
ACTIVE_WORKSPACE_FILE = CONFIG_DIR / "active_workspace"

# --- GLOBAL CONSOLE OBJECT ---
console = Console()

# --- CACHING ---
_KEY_CACHE = {}
_TEAM_KEY_CACHE = {}


def get_active_workspace_id() -> str | None:
    if ACTIVE_WORKSPACE_FILE.exists(): return ACTIVE_WORKSPACE_FILE.read_text().strip()
    return None

def set_active_workspace_id(workspace_id: str):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    ACTIVE_WORKSPACE_FILE.write_text(workspace_id)

def clear_active_workspace():
    if ACTIVE_WORKSPACE_FILE.exists(): ACTIVE_WORKSPACE_FILE.unlink(missing_ok=True)

def get_user_uid() -> str | None:
    if not auth.CREDS_FILE.exists(): return None
    try: return json.loads(auth.CREDS_FILE.read_text()).get('localId')
    except: return None

def _get_active_context(verbose: bool = False) -> tuple[Optional[str], bytes, str, str]:
    active_user = keychain.get_active_user()
    if not active_user: raise click.ClickException("Not logged in. Run 'noirnote-cli login'.")
    user_uid = get_user_uid()
    if not user_uid: raise click.ClickException("Corrupted session. Please log in again.")
    workspace_id = get_active_workspace_id() or user_uid
    id_token = auth.get_current_id_token()
    if not id_token: raise click.ClickException("Session expired. Please log in again.")
    if "private_key_pem" not in _KEY_CACHE:
        if verbose: console.print("--> Accessing keychain for cryptographic identity...", style="dim")
        keys = keychain.get_keys(active_user)
        if not keys: raise click.ClickException(f"Keys for '{active_user}' not found in OS keychain. Please log in again.")
        _KEY_CACHE["private_key_pem"] = keys[1]
    private_key_pem = _KEY_CACHE["private_key_pem"]
    if workspace_id == user_uid:
        if verbose: console.print("--> Context: Personal Workspace", style="dim")
        master_key_bytes = local_auth.derive_master_key_from_private_key(private_key_pem)
        return (None, master_key_bytes, id_token, user_uid)
    else:
        if verbose: console.print(f"--> Context: Team Workspace ({workspace_id[:8]}...)", style="dim")
        if workspace_id in _TEAM_KEY_CACHE:
            if verbose: console.print("--> Using cached team key.", style="dim")
            return (workspace_id, _TEAM_KEY_CACHE[workspace_id], id_token, user_uid)
        api_client = NoirNoteAPIClient()
        if verbose: console.print("--> Fetching team data to decrypt workspace key...", style="dim")
        teams = api_client.list_user_teams(id_token)
        target_team = next((t for t in teams if t['id'] == workspace_id), None)
        if not target_team:
            set_active_workspace_id(user_uid)
            _TEAM_KEY_CACHE.clear()
            raise click.ClickException(f"Invalid workspace '{workspace_id}'. Switched to Personal Workspace.")
        encrypted_key_b64 = target_team.get("encrypted_workspace_key")
        if not encrypted_key_b64:
            raise click.ClickException(f"Workspace key for '{target_team.get('name')}' is missing from server data.")
        if verbose: console.print("--> Decrypting workspace key...", style="dim")
        private_key_obj = crypto.deserialize_pem_to_key(private_key_pem.encode('utf-8'), is_private=True)
        encrypted_key_bytes = base64.b64decode(encrypted_key_b64)
        decryption_key_bytes = crypto.decrypt_with_private_key(private_key_obj, encrypted_key_bytes)
        _TEAM_KEY_CACHE[workspace_id] = decryption_key_bytes
        return (workspace_id, decryption_key_bytes, id_token, user_uid)

# --- NEW: WELCOME BANNER ---
def _print_welcome_banner():
    """Clears the screen and prints a stylized welcome banner."""
    octopus = r"""
     _____
   /       \
  |  >   <  |
  |   ---   |
 /  \     /  \
|   | | | |   |
 \__|_|_|_|__/

    """
    title = "N O I R N O T E"
    
    console.clear()
    console.print(Text(octopus, style="cyan"))
    console.print(Text(title, style="bold"))
    console.print()

# --- CLI COMMAND GROUP DEFINITIONS ---
@click.group()
def cli():
    """NoirNote CLI: Securely access your secrets, notes, and scripts."""
    pass

@cli.group()
def get():
    """Retrieves and decrypts items from the active workspace."""
    pass

@cli.group()
def ls():
    """Lists items in the active workspace."""
    pass

@cli.group()
def workspace():
    """Manage and switch between workspaces."""
    pass


# --- UI HELPER FUNCTIONS ---
UI_CACHE = {"workspaces": None, "notes": None, "secrets": None, "scripts": None}

def clear_ui_cache():
    global UI_CACHE
    UI_CACHE = {key: None for key in UI_CACHE}

def _get_status_bar_text() -> Text:
    """Generates the text for the UI status bar using Rich Text."""
    try:
        active_user = keychain.get_active_user() or "Unknown"
        if active_user == 'api-key-user':
            return Text.assemble(("🔑 ", "yellow"), ("API Key Mode", "bold yellow"))
            
        team_id, _, id_token, user_uid = _get_active_context()
        workspace_name = "Personal Workspace"

        if team_id:
            if UI_CACHE.get("workspaces"):
                team_info = next((ws for ws in UI_CACHE["workspaces"] if ws.get('id') == team_id), None)
                if team_info: workspace_name = team_info.get('name', 'Unknown Workspace')
            else:
                api_client = NoirNoteAPIClient()
                teams = api_client.list_user_teams(id_token)
                team_info = next((t for t in teams if t['id'] == team_id), None)
                if team_info: workspace_name = team_info.get('name', 'Unknown Workspace')
        
        status_text = Text.assemble(
            ("👤 ", "white"),
            (active_user, "bold white"),
            ("  |  ", "dim"),
            ("🌐 ", "cyan"),
            (workspace_name, "bold cyan")
        )
        return status_text
    except Exception:
        return Text("Error fetching status...", style="bold red")

def handle_notes_menu():
    ctx = click.get_current_context()
    api_client = NoirNoteAPIClient()
    team_id, _, id_token, _ = _get_active_context()
    if UI_CACHE["notes"] is None:
        console.print("--> Fetching notes for the active workspace...", style="dim")
        UI_CACHE["notes"] = api_client.list_notes(id_token, team_id=team_id)
    if not UI_CACHE["notes"]:
        console.print("No notes found in this workspace.", style="yellow")
        questionary.press_any_key_to_continue().ask()
        return

    note_choices = [
        questionary.Separator(f"{'NOTE NAME':<50} {'NOTE ID'}"),
    ]
    for note_item in UI_CACHE["notes"]:
        title = f"{note_item.get('name', 'N/A'):<50} {note_item.get('id')}"
        note_choices.append(Choice(title=title, value=note_item['id']))

    note_choices.append(questionary.Separator())
    note_choices.append(Choice(title="<-- Back", value="back"))
    
    selected_note_id = questionary.select(
        "Select a note:", 
        choices=note_choices, 
        use_indicator=True,
        pointer="»"
    ).ask()

    if selected_note_id and selected_note_id != 'back':
        _print_welcome_banner()
        ctx.invoke(get_note, name_or_id=selected_note_id)
        questionary.press_any_key_to_continue().ask()

def handle_secrets_menu():
    ctx = click.get_current_context()
    api_client = NoirNoteAPIClient()
    team_id, decryption_key, id_token, _ = _get_active_context()
    if UI_CACHE["secrets"] is None:
        console.print("--> Fetching and decrypting secret index...", style="dim")
        secret_index_raw = api_client.get_secret_index(id_token, team_id=team_id)
        decrypted_secrets = []
        for meta in secret_index_raw:
            try:
                name = crypto.decrypt_secret(decryption_key, meta['encrypted_name'], meta['name_tag'])
                decrypted_secrets.append({"id": meta['id'], "name": name})
            except Exception:
                decrypted_secrets.append({"id": meta['id'], "name": "[DECRYPTION ERROR]"})
        UI_CACHE["secrets"] = decrypted_secrets
    if not UI_CACHE["secrets"]:
        console.print("No secrets found in this workspace.", style="yellow")
        questionary.press_any_key_to_continue().ask()
        return
    
    secret_choices = [questionary.Separator(f"{'SECRET NAME':<40} {'SECRET ID'}")]
    for s in UI_CACHE["secrets"]:
        title = f"{s['name']:<40} {s['id']}"
        secret_choices.append(Choice(title=title, value=s['id']))
    
    secret_choices.append(questionary.Separator())
    secret_choices.append(Choice(title="<-- Back", value="back"))

    selected_secret_id = questionary.select(
        "Select a secret to view:", 
        choices=secret_choices,
        pointer="»"
    ).ask()

    if selected_secret_id and selected_secret_id != 'back':
        _print_welcome_banner()
        ctx.invoke(get_secret, secret_id_or_name=selected_secret_id)
        console.print()
        questionary.press_any_key_to_continue().ask()

def handle_workspaces_menu():
    ctx = click.get_current_context()
    api_client = NoirNoteAPIClient()
    _, _, id_token, user_uid = _get_active_context()
    if UI_CACHE["workspaces"] is None:
        console.print("--> Fetching available workspaces...", style="dim")
        remote_teams = api_client.list_user_teams(id_token)
        all_workspaces = {team['id']: team for team in remote_teams}
        all_workspaces[user_uid] = {"id": user_uid, "name": "Personal Workspace", "role": "Owner"}
        UI_CACHE["workspaces"] = sorted(all_workspaces.values(), key=lambda x: x.get('name', ''))
    
    current_ws_id = get_active_workspace_id() or user_uid
    ws_choices = []
    for ws in UI_CACHE["workspaces"]:
        is_active = "✅" if ws['id'] == current_ws_id else "  "
        title = f"{is_active} {ws['name']:<30} ({ws['role']})"
        ws_choices.append(Choice(title=title, value=ws['id']))

    ws_choices.append(questionary.Separator())
    ws_choices.append(Choice(title="<-- Back", value="back"))
    selected_ws_id = questionary.select("Select a workspace to switch to:", choices=ws_choices).ask()
    if selected_ws_id and selected_ws_id != 'back' and selected_ws_id != current_ws_id:
        ctx.invoke(workspace_use, name_or_id=selected_ws_id)
        clear_ui_cache()

def handle_scripts_menu():
    ctx = click.get_current_context()
    api_client = NoirNoteAPIClient()
    team_id, _, id_token, _ = _get_active_context()
    if UI_CACHE["scripts"] is None:
        console.print("--> Fetching scripts for the active workspace...", style="dim")
        UI_CACHE["scripts"] = api_client.get_script_library_index(id_token, team_id=team_id)
    if not UI_CACHE["scripts"]:
        console.print("No scripts found in this workspace.", style="yellow")
        questionary.press_any_key_to_continue().ask()
        return

    script_choices = [
        questionary.Separator(f"{'SCRIPT NAME':<50} {'SCRIPT ID'}"),
    ]
    for script_item in UI_CACHE["scripts"]:
        title = f"{script_item.get('name', 'N/A'):<50} {script_item.get('id')}"
        script_choices.append(Choice(title=title, value=script_item['id']))

    script_choices.append(questionary.Separator())
    script_choices.append(Choice(title="<-- Back", value="back"))
    
    selected_script_id = questionary.select(
        "Select a script to execute:",
        choices=script_choices,
        pointer="»"
    ).ask()

    if selected_script_id and selected_script_id != 'back':
        selected_script_name = next(s['name'] for s in UI_CACHE["scripts"] if s['id'] == selected_script_id)
        confirm = questionary.confirm(f"Are you sure you want to run '{selected_script_name}'?").ask()
        if confirm:
            _print_welcome_banner()
            ctx.invoke(run_exec, name=selected_script_name, yes=True)
            questionary.press_any_key_to_continue().ask()

@cli.command()
def ui():
    """Starts an interactive UI session for a more convenient workflow."""
    try:
        if auth.get_api_credentials():
            console.print("[yellow]CLI is in API Key mode. Interactive UI is disabled.[/]")
            console.print("Run 'noirnote-cli logout' to clear API key configuration and re-enable interactive login.")
            return
        _get_active_context(verbose=False)
        _print_welcome_banner()
    except Exception as e:
        console.print(Panel(f"Failed to start interactive session: {e}", title="[bold red]Error[/]", border_style="red"))
        return

    while True:
        try:
            console.print(_get_status_bar_text())
            console.print() # Spacer
            
            action = questionary.select(
                message="Main Menu:",
                choices=[
                    Choice("▶️  Scripts", value="scripts"),
                    Choice("📝 Notes", value="notes"),
                    Choice("🔐 Secrets", value="secrets"),
                    Choice("🌐 Workspaces", value="workspaces"),
                    questionary.Separator(),
                    Choice("🚪 Exit", value="exit")
                ],
                use_indicator=True,
                style=questionary.Style([('pointer', 'bold fg:#00d1ff')])
            ).ask()

            if action is None or action == "exit":
                console.print("\nExiting interactive session.")
                break

            _print_welcome_banner()

            if action == "scripts": handle_scripts_menu()
            elif action == "notes": handle_notes_menu()
            elif action == "secrets": handle_secrets_menu()
            elif action == "workspaces": handle_workspaces_menu()

        except (KeyboardInterrupt, EOFError):
            console.print("\nExiting interactive session.")
            break
        except Exception as e:
            _print_welcome_banner()
            console.print(Panel(f"An unexpected error occurred:\n\n{e}", title="[bold red]Critical Error[/]", border_style="red"))
            traceback.print_exc(file=sys.stderr)
            questionary.press_any_key_to_continue().ask()
            _print_welcome_banner()

@cli.command()
@click.option('--api-key', required=True, help="Your API Key ID.")
@click.option('--api-secret', required=True, help="Your Secret Access Key.")
def configure(api_key, api_secret):
    """Configures the CLI for non-interactive use with an API Key."""
    try:
        active_user = keychain.get_active_user()
        if active_user and active_user != 'api-key-user':
            console.print(f"Removing existing interactive login for [yellow]{active_user}[/]...", style="dim")
            keychain.delete_keys(active_user)
        
        auth.clear_firebase_creds()
        auth.store_api_credentials(api_key, api_secret)
        keychain.set_active_user('api-key-user')
        
        console.print("[green]Success![/] CLI has been configured for non-interactive use.")
        console.print("You can now use commands like 'get secret' in your scripts.", style="dim")
    except Exception as e:
        console.print(Panel(f"Configuration failed:\n\n{e}", title="[bold red]Error[/]", border_style="red"))
        sys.exit(1)

@cli.command()
@click.option('--email', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
def login(email, password):
    """Logs in an interactive user."""
    if auth.get_api_credentials():
        console.print("[yellow]CLI is in API Key mode. Login is disabled.[/]")
        console.print("Run 'noirnote-cli logout' to clear API key configuration.")
        return
        
    email = email.strip().lower()
    api_client = NoirNoteAPIClient()
    try:
        console.print("--> Authenticating with Firebase...", style="dim")
        firebase_api_key = "AIzaSyB6h6Aky5wtJTw1-xglMaago93k_KSXoXM"
        rest_api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"email": email, "password": password, "returnSecureToken": True}
        try:
            response = requests.post(rest_api_url, headers=headers, json=payload, timeout=20)
            response.raise_for_status()
            user_creds = response.json()
        except requests.exceptions.HTTPError as e:
            try:
                error_data = e.response.json().get("error", {})
                message = error_data.get("message", "Invalid credentials or connection error.")
                if "INVALID_LOGIN_CREDENTIALS" in message or "EMAIL_NOT_FOUND" in message or "INVALID_PASSWORD" in message:
                    raise ValueError("Invalid email or password.")
                raise Exception(f"Firebase Auth Error: {message}")
            except (json.JSONDecodeError, AttributeError):
                raise Exception(f"API Error ({e.response.status_code}): {e.response.text}") from e
        id_token, user_uid = user_creds['idToken'], user_creds['localId']
        console.print("--> Firebase authentication successful.", style="dim")
        console.print("--> Fetching secure client configuration...", style="dim")
        full_firebase_config = api_client.get_firebase_cli_config(id_token)
        auth.store_firebase_creds(email, user_creds, full_firebase_config)
        user_data = local_auth.load_user_data(email)
        if user_data:
            console.print("--> Local settings found. Decrypting keys with password...", style="dim")
            private_key_pem = local_auth.decrypt_private_key_from_local_data(user_data, password)
        else:
            console.print("--> No local settings found. New device login required.", style="dim")
            recovery_key_b64 = click.prompt("Please enter your Master Recovery Key", hide_input=True)
            console.print("--> Fetching cloud-stored key backup...", style="dim")
            public_auth_data = api_client.get_user_public_auth_data(id_token)
            encrypted_pk_A_b64 = public_auth_data['encrypted_private_key_A']
            console.print("--> Decrypting private key with Master Recovery Key...", style="dim")
            recovery_key_bytes = base64.b64decode(recovery_key_b64)
            aesgcm = AESGCM(recovery_key_bytes)
            encrypted_payload_A = base64.b64decode(encrypted_pk_A_b64)
            nonce, ciphertext_with_tag = encrypted_payload_A[:12], encrypted_payload_A[12:]
            private_key_pem_bytes = aesgcm.decrypt(nonce, ciphertext_with_tag, None)
            private_key_pem = private_key_pem_bytes.decode('utf-8')
            console.print("--> Creating new local settings file...", style="dim")
            local_auth.save_local_user_file(email, password, user_uid, private_key_pem)
        console.print("--> Deriving personal master key...", style="dim")
        master_key_bytes = local_auth.derive_master_key_from_private_key(private_key_pem)
        master_key_b64 = base64.b64encode(master_key_bytes).decode('utf-8')
        console.print("--> Storing cryptographic identity in OS keychain...", style="dim")
        keychain.store_keys(email, master_key_b64, private_key_pem)
        keychain.set_active_user(email)
        set_active_workspace_id(user_uid)
        console.print(f"\n[green]Success![/] Logged in as [bold]{email}[/]. Personal workspace is active.")
    except (ValueError, InvalidTag) as e:
        console.print(f"[red]Login failed:[/] {e}")
        auth.clear_firebase_creds()
        keychain.clear_active_user()
        sys.exit(1)
    except Exception as e:
        console.print(Panel(f"A critical error occurred during login:\n\n{e}", title="[bold red]Error[/]", border_style="red"))
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

@cli.command()
def logout():
    """Logs out the interactive user or clears API key configuration."""
    active_user = keychain.get_active_user()
    if not active_user:
        console.print("Not logged in or configured.")
        return

    if active_user == 'api-key-user':
        if questionary.confirm("This will remove the API key configuration. Are you sure?").ask():
            auth.clear_firebase_creds()
            keychain.clear_active_user()
            console.print("[green]API key configuration has been removed.[/]")
    else:
        if questionary.confirm(f"Are you sure you want to log out {active_user}?").ask():
            keychain.delete_keys(active_user)
            keychain.clear_active_user()
            auth.clear_firebase_creds()
            clear_active_workspace()
            local_settings_file = local_auth._get_user_settings_path(active_user)
            if local_settings_file.exists():
                local_settings_file.unlink()
                console.print("--> Removed local settings file.", style="dim")
            console.print(f"[green]Successfully logged out {active_user}.[/]")

@get.command(name="note")
@click.argument('name_or_id')
def get_note(name_or_id):
    """Retrieves and decrypts a note by its name or ID."""
    try:
        team_id, decryption_key, id_token, _ = _get_active_context()
        api_client = NoirNoteAPIClient()
        target_note_id, note_name = None, name_or_id
        
        try:
            payload = api_client.get_note_payload(id_token, name_or_id, team_id=team_id)
            target_note_id = name_or_id
            all_notes = api_client.list_notes(id_token, team_id=team_id)
            found_note = next((n for n in all_notes if n['id'] == target_note_id), None)
            if found_note: note_name = found_note['name']

        except Exception:
            matches = api_client.find_note_by_name(id_token, name_or_id, team_id=team_id)
            if len(matches) == 1:
                target_note_id = matches[0]['id']
                note_name = matches[0]['name']
            elif len(matches) > 1:
                console.print("[yellow]Error: Multiple notes found. Use a unique ID.[/]")
                sys.exit(1)
            else:
                raise click.ClickException(f"No note found with name or ID '{name_or_id}'.")
        
        if not target_note_id: raise click.ClickException("Could not resolve note.")
        
        if 'payload' not in locals():
            payload = api_client.get_note_payload(id_token, target_note_id, team_id=team_id)
            
        plaintext_html = crypto.decrypt_secret(decryption_key, payload['ciphertext'], payload['tag'])
        cleaned_text = _clean_html(plaintext_html)
        
        console.print(Panel(cleaned_text, title=f"📝 {note_name}", border_style="cyan", expand=False))

    except Exception as e:
        console.print(f"[red]Failed to get note:[/] {e}")
        sys.exit(1)

@get.command(name="secret")
@click.argument('secret_id_or_name', required=False)
def get_secret(secret_id_or_name):
    """
    Retrieves a secret. In API mode, fetches the key's assigned secret.
    In interactive mode, requires a secret name or ID.
    """
    api_client = NoirNoteAPIClient()
    api_creds = auth.get_api_credentials()
    
    if api_creds:
        api_key_id, secret_access_key = api_creds
        try:
            if secret_id_or_name:
                console.print(f"Note: Argument '{secret_id_or_name}' is ignored in API key mode.", style="yellow")
            
            console.print("--> Fetching secret using API key...", style="dim", file=sys.stderr)
            encrypted_value, tag = api_client.get_encrypted_payload(api_key_id)
            secret_key_bytes = base64.b64decode(secret_access_key)
            plaintext_secret = crypto.decrypt_secret(secret_key_bytes, encrypted_value, tag)
            click.echo(plaintext_secret, nl=False)
        except Exception as e:
            console.print(f"[red]Failed to get secret via API key:[/] {e}", file=sys.stderr)
            sys.exit(1)
    else:
        if not secret_id_or_name:
            console.print("[red]Error:[/] A secret name or ID is required in interactive mode.")
            sys.exit(1)
        try:
            team_id, decryption_key, id_token, _ = _get_active_context()
            payload = None
            try:
                payload = api_client.get_vault_secret_payload(id_token, secret_id_or_name, team_id=team_id)
            except Exception:
                index = api_client.get_secret_index(id_token, team_id=team_id)
                for item in index:
                    try:
                        name = crypto.decrypt_secret(decryption_key, item['encrypted_name'], item['name_tag'])
                        if name.lower() == secret_id_or_name.lower():
                            payload = api_client.get_vault_secret_payload(id_token, item['id'], team_id=team_id)
                            break
                    except:
                        continue
                if not payload:
                    raise click.ClickException(f"No secret found with name or ID '{secret_id_or_name}'.")
            secret_name = crypto.decrypt_secret(decryption_key, payload['encrypted_name'], payload['name_tag'])
            secret_value = crypto.decrypt_secret(decryption_key, payload['encrypted_value'], payload['value_tag'])
            console.print(Panel(secret_value, title=f"🔐 Secret: {secret_name}", border_style="green", expand=False))
        except Exception as e:
            console.print(f"[red]Failed to get secret:[/] {e}", file=sys.stderr)
            sys.exit(1)

@ls.command(name="secrets")
def ls_secrets():
    """Lists secrets in the current workspace."""
    try:
        team_id, decryption_key, id_token, _ = _get_active_context()
        api_client = NoirNoteAPIClient()
        secret_index_raw = api_client.get_secret_index(id_token, team_id=team_id)
        if not secret_index_raw:
            console.print("No secrets found in this workspace.", style="yellow")
            return
        table = Table(title="Vault Secrets")
        table.add_column("Secret Name", style="cyan", no_wrap=True)
        table.add_column("Secret ID", style="magenta")
        for meta in secret_index_raw:
            try:
                name = crypto.decrypt_secret(decryption_key, meta['encrypted_name'], meta['name_tag'])
                table.add_row(name, meta['id'])
            except:
                table.add_row("[DECRYPTION ERROR]", meta['id'], style="red")
        console.print(table)
    except Exception as e:
        console.print(f"[red]Failed to list secrets:[/] {e}")
        sys.exit(1)

@ls.command(name="notes")
def ls_notes():
    """Lists notes in the current workspace."""
    try:
        team_id, _, id_token, _ = _get_active_context()
        api_client = NoirNoteAPIClient()
        note_library = api_client.list_notes(id_token, team_id=team_id)
        if not note_library:
            console.print("No notes found in this workspace.", style="yellow")
            return
        table = Table(title="Note Library")
        table.add_column("Note Name", style="cyan", no_wrap=True)
        table.add_column("Note ID", style="magenta")
        for note_item in note_library:
            table.add_row(note_item.get('name', 'N/A'), note_item.get('id'))
        console.print(table)
    except Exception as e:
        console.print(f"[red]Failed to list notes:[/] {e}")
        sys.exit(1)

@workspace.command("list")
def workspace_list():
    """Lists available workspaces for the logged-in user."""
    try:
        _, _, id_token, user_uid = _get_active_context()
        api_client = NoirNoteAPIClient()
        teams = api_client.list_user_teams(id_token)
        table = Table(title="Available Workspaces")
        table.add_column("Workspace Name", style="cyan")
        table.add_column("ID", style="magenta")
        table.add_column("Role", style="yellow")
        table.add_row("Personal Workspace", user_uid, "Owner")
        for team in sorted(teams, key=lambda x: x.get('name', '')):
            table.add_row(team.get('name', 'N/A'), team.get('id', 'N/A'), team.get('role', 'N/A').capitalize())
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        sys.exit(1)

@workspace.command("use")
@click.argument("name_or_id")
def workspace_use(name_or_id):
    """Switches the active workspace."""
    try:
        _, _, id_token, user_uid = _get_active_context()
        api_client = NoirNoteAPIClient()
        teams = api_client.list_user_teams(id_token)
        teams.append({"id": user_uid, "name": "Personal Workspace", "role": "Owner"})
        target_workspace = next((t for t in teams if t['id'] == name_or_id), None)
        if not target_workspace:
            target_workspace = next((t for t in teams if t['name'].lower() == name_or_id.lower()), None)
        if not target_workspace: raise click.ClickException(f"Workspace '{name_or_id}' not found.")
        set_active_workspace_id(target_workspace['id'])
        console.print(f"Switched to workspace: [cyan]{target_workspace['name']}[/]")
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        sys.exit(1)

@cli.command(name="exec")
@click.option('--name', help="Directly execute a script by its exact name.")
@click.option('--yes', is_flag=True, help="Skip the final confirmation prompt.")
def run_exec(name, yes):
    """Executes a script from the current workspace."""
    try:
        team_id, decryption_key, id_token, _ = _get_active_context()
        api_client = NoirNoteAPIClient()
        target_script_id, target_script_name = None, "Selected Script"
        library = api_client.get_script_library_index(id_token, team_id=team_id)
        if not library: raise click.ClickException("No scripts found in this workspace.")
        if name:
            found_script = next((s for s in library if s['name'] == name), None)
            if not found_script: raise click.ClickException(f"No script named '{name}' found.")
            target_script_id, target_script_name = found_script['id'], found_script['name']
        else:
            choices = [s['name'] for s in library]
            selected_script_name = questionary.select("Select a script to execute:", choices=choices).ask()
            if not selected_script_name: return
            found_script = next((s for s in library if s['name'] == selected_script_name), None)
            target_script_id, target_script_name = found_script['id'], found_script['name']
        if not yes:
            if not click.confirm(f"Are you sure you want to run '{target_script_name}'?"): return
        console.print(f"--> Fetching script '{target_script_name}'...", style="dim")
        encrypted_payload = api_client.get_script_payload(id_token, target_script_id, team_id=team_id)
        script_content = crypto.decrypt_secret(decryption_key, encrypted_payload['ciphertext'], encrypted_payload['tag'])
        console.print(f"--> Executing script: {target_script_name}", style="green")
        console.print(Panel(Syntax(script_content, "bash", theme="monokai", line_numbers=True), title="Script Content"))
        subprocess.run(script_content, shell=True, check=True, text=True)
    except Exception as e:
        console.print(f"[red]Execution failed:[/] {e}")
        sys.exit(1)

def _clean_html(raw_html: str) -> str:
    import re
    clean_re = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    text = re.sub(clean_re, '', raw_html)
    return text.strip()

if __name__ == '__main__':
    cli()