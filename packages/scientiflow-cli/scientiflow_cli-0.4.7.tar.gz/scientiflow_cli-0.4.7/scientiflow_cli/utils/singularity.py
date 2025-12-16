import subprocess
from pathlib import Path

import requests
from rich.console import Console
from scientiflow_cli.services.rich_printer import RichPrinter

console = Console()
printer = RichPrinter()

SINGULARITY_VERSION = "4.2.1"

def run_command(command, check=True):
    try:
        result = subprocess.run(
            command,
            check=check,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result
    except subprocess.CalledProcessError as e:
        printer.print_message(f"[bold red]Error running command:[/bold red] {' '.join(command)}\n{e.stderr}")
        raise


def command_exists(command):
    result = subprocess.run(
        ["which", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    return result.returncode == 0


def install_singularity():
    if command_exists("singularity"):
        printer.print_message("[bold green][+] Singularity is already installed.[/bold green]")
        return

    printer.print_message("[bold yellow][+] Installing Singularity[/bold yellow]")
    os_release_path = Path("/etc/os-release")
    os_codename = None

    if os_release_path.exists():
        for line in os_release_path.read_text().splitlines():
            if line.startswith("VERSION_CODENAME="):
                os_codename = line.split("=")[1]
                break

    if not os_codename:
        raise ValueError("[bold red]Could not determine Ubuntu / Debian codename from /etc/os-release.[/bold red]")
    
    if os_codename == "bookworm":
        printer.print_message("[bold yellow][+] WARNING: Debian distros are not officially supported. Compatibility issues may arise[/bold yellow]")
        os_codename = "jammy"

    singularity_url = f"https://github.com/sylabs/singularity/releases/download/v{SINGULARITY_VERSION}/singularity-ce_{SINGULARITY_VERSION}-{os_codename}_amd64.deb"
    temp_file = Path(f"/tmp/singularity-ce_{SINGULARITY_VERSION}-{os_codename}_amd64.deb")

    printer.print_message("[bold cyan]Downloading Singularity package...[/bold cyan]")
    progress, task = printer.create_progress_bar("[cyan]Downloading...", total=100)
    response = requests.get(singularity_url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get("content-length", 0))
    downloaded = 0
    with open(temp_file, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            progress.update(task, advance=(downloaded / total_size) * 100)

    printer.print_message("[bold cyan]Installing Singularity...[/bold cyan]")
    progress, task = printer.create_progress_bar("[cyan]Installing...", total=1)
    subprocess.run(["sudo", "apt", "install", "-y", "-f", str(temp_file)], check=True)
    progress.update(task, advance=1)
    temp_file.unlink()
    printer.print_message("[bold green]Installation complete[/bold green]")


def install_nvidia_container_toolkit():
    printer.print_message("[bold yellow][+] Installing NVIDIA Container Toolkit...[/bold yellow]")
    run_command(
        ["bash", "-c", "curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg"]
    )
    run_command(
        ["bash", "-c", "curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list"]
    )
    run_command(["sudo", "apt-get", "update"])
    run_command(["sudo", "apt-get", "install", "-y", "nvidia-container-toolkit"])
    printer.print_message("[bold green][+] NVIDIA Container Toolkit installed successfully![/bold green]")


def enable_gpu_support():
    printer.print_message("[bold yellow][+] Enabling GPU support for Singularity...[/bold yellow]")
    if not command_exists("nvidia-container-cli"):
        printer.print_message("[bold red]NVIDIA Container Toolkit is not installed. Installing it now...[/bold red]")
        install_nvidia_container_toolkit()
    run_command(["sudo", "sed", "-i", "s/^use nvidia-container-cli = no$/use nvidia-container-cli = yes/", "/etc/singularity/singularity.conf"])
    run_command(["sudo", "sed", "-i", "s|^# nvidia-container-cli path =|nvidia-container-cli path = /usr/bin/nvidia-container-cli|", "/etc/singularity/singularity.conf"])


def install_singularity_main(enable_gpu=False, nvccli=False):
    install_singularity()
    if enable_gpu:
        enable_gpu_support()
    if nvccli:
        if not command_exists("nvidia-container-cli"):
            printer.print_message("[bold red]NVIDIA Container Toolkit is not installed. Installing it now...[/bold red]")
            install_nvidia_container_toolkit()


if __name__ == "__main__":
    install_singularity_main()

