import os
from cryptography.fernet import Fernet
from rich.console import Console
from rich.panel import Panel

TOKEN_FILE_PATH = os.path.expanduser("~/.scientiflow/token")
KEY_FILE_PATH = os.path.expanduser("~/.scientiflow/key")

console = Console()

def setAuthToken(auth_token):
    try:
        directory = os.path.dirname(TOKEN_FILE_PATH)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        if not os.path.exists(KEY_FILE_PATH):
            key = Fernet.generate_key()
            with open(KEY_FILE_PATH, "wb") as key_file:
                key_file.write(key)
            os.chmod(KEY_FILE_PATH, 0o600)
        else:
            with open(KEY_FILE_PATH, "rb") as key_file:
                key = key_file.read()

        fernet = Fernet(key)
        encrypted_token = fernet.encrypt(auth_token.encode())

        with open(TOKEN_FILE_PATH, "wb") as token_file:
            token_file.write(encrypted_token)
        os.chmod(TOKEN_FILE_PATH, 0o600)

        console.print("[bold green]Token encrypted and saved securely.[/bold green]")
    except Exception as e:
        print(f"Error setting auth token: {e}")

def getAuthToken():
    if os.path.exists(TOKEN_FILE_PATH) and os.path.exists(KEY_FILE_PATH):
        try:
            with open(KEY_FILE_PATH, 'rb') as key_file:
                encryption_key = key_file.read()
            
            fernet = Fernet(encryption_key)
            
            with open(TOKEN_FILE_PATH, 'rb') as token_file:
                encrypted_token = token_file.read()
            
            token = fernet.decrypt(encrypted_token).decode()
            return token
        except Exception as e:
            print(f"Failed to decrypt token: {e}")
            return None
    else:
        return None