import os
import json
from scientiflow_cli.services.request_handler import make_auth_request
from scientiflow_cli.services.rich_printer import RichPrinter
from rich.prompt import Prompt

printer = RichPrinter()

def set_base_directory(hostname: str = None, base_dir_path: str = None) -> None:
    if not hostname:
        hostname = Prompt.ask("[bold cyan]Enter the hostname for this[/bold cyan]")
    
    if base_dir_path:
        base_directory = base_dir_path
    else:
        base_directory = os.getcwd()

    # sends a request to the create-server endpoint
    body = {
      "hostname": hostname,
      "base_directory": base_directory,
      "description": ""
    }
    
    try:
        make_auth_request(endpoint="/servers/create-or-update-server", method="POST", data=body, error_message="Unable to set base directory!")
        # stores the current working directory and hostname in a .config file
        config_path = os.path.expanduser("~/.scientiflow/config")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as file:
            file.write(json.dumps({"BASE_DIR": base_directory, "HOSTNAME": hostname}))
        printer.print_message("Successfully set base directory!", style="bold green")
    except Exception as e:
        printer.print_panel(f"Error: {e}", style="bold red")
    return

def get_base_directory() -> str:
    """Retrieve the base directory path saved in the configuration file."""
    config_path = os.path.expanduser("~/.scientiflow/config")
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as file:
                config = json.load(file)
                return config.get("BASE_DIR", "")
        else:
            printer.print_error(f"Base directory not set: Please set it using the command: scientiflow-cli --set-base-directory")
            return ""
    except Exception as e:
        printer.print_error(f"Base directory not set: Please set it using the command: scientiflow-cli --set-base-directory")
        return ""

def get_hostname() -> str:
    """Retrieve the hostname saved in the configuration file."""
    config_path = os.path.expanduser("~/.scientiflow/config")
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as file:
                config = json.load(file)
                return config.get("HOSTNAME", "")
        else:
            printer.print_error(f"Hostname not set: Please set it using the command: scientiflow-cli --set-base-directory")
            return ""
    except Exception as e:
        printer.print_error(f"Hostname not set: Please set it using the command: scientiflow-cli --set-base-directory")
        return ""
