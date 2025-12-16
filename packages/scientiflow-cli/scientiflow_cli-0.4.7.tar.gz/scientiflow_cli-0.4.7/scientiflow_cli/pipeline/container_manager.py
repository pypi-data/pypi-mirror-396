import subprocess
from pathlib import Path
from scientiflow_cli.services.request_handler import make_auth_request
from scientiflow_cli.services.rich_printer import RichPrinter
from scientiflow_cli.services.base_directory import get_base_directory
from rich.prompt import Prompt

printer = RichPrinter()

def get_available_containers(containers_dir: Path) -> set[str]:
    """
    Return a set of available container file names in the given directory.
    """
    return {item.name for item in containers_dir.iterdir() if item.is_file()}

def get_job_containers(job: dict) -> None:
    base_dir = Path(job['server']['base_directory'])
    containers_dir = base_dir / "containers"
    project_job_id = job['project_job']['id']
    if not containers_dir.exists():
        containers_dir.mkdir()

    # Get names of containers already available in the user's machine
    avail_containers: set[str] = get_available_containers(containers_dir)
    params = {"project_job_id": project_job_id}
    response = make_auth_request(endpoint="/agent-application/get-user-containers", method="GET", params=params, error_message="Unable to get containers info!")
    try:
        if response.status_code == 200:
            container_info = response.json()

            if not container_info:
                printer.print_message("No containers found for current User / Project", style="bold red")
                return

            current_pipeline_containers = set(container_info["current_pipeline_containers"])

            # Download containers which are not present on the user's machine
            containers_to_download = current_pipeline_containers - avail_containers

            progress, task = printer.create_progress_bar("[cyan]Downloading containers...", total=len(containers_to_download))
            for container_name in container_info['container_image_details']:
                if container_name['image_name'] in containers_to_download:
                    container_path = containers_dir / f"{container_name['image_name']}.sif"
                    if container_path.exists():
                        printer.print_message(f"[~] Using cached image: {container_name['image_name']}", style="bold yellow")
                        progress.update(task, advance=1)
                        continue  # Skip downloading if the file already exists

                    command = f"singularity pull {container_name['image_name']}.sif {container_name['sylabs_uri']}"
                    printer.print_message(f"[+] Downloading container: {container_name['image_name']}", style="bold green")
                    try:
                        process = subprocess.Popen(
                            command,
                            cwd=containers_dir,
                            shell=True
                        )
                        process.communicate()
                        if process.returncode == 0:
                            progress.update(task, advance=1)
                        else:
                            raise subprocess.CalledProcessError(process.returncode, command)
                    except subprocess.CalledProcessError as e:
                        printer.print_panel(
                            f"Failed to download container: {container_name['image_name']}\n"
                            f"Command: {command}\n"
                            f"Error Code: {e.returncode}",
                            style="bold red"
                        )

    except subprocess.CalledProcessError:
        printer.print_message("Error executing singularity commands. Try checking your singularity installation", style="bold red")
        return

    except Exception as e:
        printer.print_panel(f"Error: {e}", style="bold red")

def manage_containers(base_dir: str, job: dict = None) -> None:
    containers_dir = Path(base_dir) / "containers"
    if not containers_dir.exists():
        containers_dir.mkdir()

    # Get names of containers already available in the user's machine
    avail_containers: set[str] = get_available_containers(containers_dir)

    if job:
        project_job_id = job['project_job']['id']
        params = {"project_job_id": project_job_id}
        response = make_auth_request(endpoint="/agent-application/get-user-containers", method="GET", params=params, error_message="Unable to get containers info!")
        try:
            if response.status_code == 200:
                container_info = response.json()

                if not container_info:
                    printer.print_message("No containers found for current User / Project", style="bold red")
                    return

                user_all_containers = set(container_info["user_all_unique_containers"])

                # Identify containers that are not needed
                containers_to_remove = avail_containers - user_all_containers

                if containers_to_remove:
                    printer.print_message("The following containers are not required:", style="bold yellow")
                    for idx, container_name in enumerate(containers_to_remove, start=1):
                        printer.print_message(f"{idx}. {container_name}", style="bold white")

                    selected_indices = Prompt.ask(
                        "Enter the numbers of the containers you want to delete (space-separated)",
                        default="",
                    )

                    try:
                        selected_indices = [int(idx.strip()) for idx in selected_indices.split() if idx.strip().isdigit()]
                        results = delete_selected_containers(containers_dir, list(containers_to_remove), selected_indices)
                        for res in results:
                            if res["status"] == "success":
                                printer.print_message(res["message"], style="bold green")
                            else:
                                printer.print_message(res["message"], style="bold red")
                    except ValueError:
                        printer.print_message("Invalid input. No containers were deleted.", style="bold red")

        except Exception as e:
            printer.print_panel(f"Error: {e}", style="bold red")
    else:
        if not avail_containers:
            printer.print_message(f"No containers found in the base directory.", style="bold red")
            return

        printer.print_message("The following containers are available:", style="bold yellow")
        for idx, container_name in enumerate(avail_containers, start=1):
            printer.print_message(f"{idx}. {container_name}", style="bold white")

        selected_indices = Prompt.ask(
            "Enter the numbers of the containers you want to delete (space-separated)",
            default="",
        )

        try:
            selected_indices = [int(idx.strip()) for idx in selected_indices.split() if idx.strip().isdigit()]
            results = delete_selected_containers(containers_dir, list(avail_containers), selected_indices)
            for res in results:
                if res["status"] == "success":
                    printer.print_message(res["message"], style="bold green")
                else:
                    printer.print_message(res["message"], style="bold red")
        except ValueError:
            printer.print_message("Invalid input. No containers were deleted.", style="bold red")

def delete_selected_containers(containers_dir: Path, container_names: list[str], selected_indices: list[int]) -> list[dict]:
    """
    Delete containers by their indices from the given list of container names.
    Indices are 1-based as shown to the user.
    Returns a list of dictionaries with 'status' and 'message' for each attempted deletion.
    """
    results = []
    for idx in selected_indices:
        if 1 <= idx <= len(container_names):
            container_name = list(container_names)[idx - 1]
            container_path = containers_dir / container_name
            try:
                container_path.unlink()
                results.append({"status": "success", "message": f"[-] Removed container: {container_name}"})
            except Exception as e:
                results.append({"status": "error", "message": f"Failed to remove {container_name}: {e}"})
        else:
            results.append({"status": "invalid", "message": f"Invalid selection: {idx}"})
    return results


