import io
import tarfile
from pathlib import Path
from scientiflow_cli.services.request_handler import make_auth_request
from scientiflow_cli.services.rich_printer import RichPrinter
from rich.progress import Progress

printer = RichPrinter()

def get_job_files(job: dict) -> None:
    base_dir: str =  job['server']['base_directory']
    project_job_id = job['project_job']['id']
    project_name = job['project']['project_title']
    job_dir = job['project_job']['job_directory']

    params = { "project_job_id": project_job_id }

    printer.print_message("Attempting to fetch user files", style="bold cyan")
    response = make_auth_request(endpoint="/agent-application/get-tar-gz-file", method="GET", params=params, error_message="Unable to fetch user files!")
    printer.print_success("[+] Completed fetching user files")

    project_dir_name = Path(base_dir) / project_name
    job_dir_name = project_dir_name / job_dir
    job_dir_name.mkdir(parents=True, exist_ok=True)

    printer.print_message("Extracting user files", style="bold cyan")
    tar_data = io.BytesIO(response.content)

    with tarfile.open(fileobj=tar_data, mode="r:gz") as tar:
        progress, task = printer.create_progress_bar("[cyan]Extracting files...", total=len(tar.getmembers()))
        for member in tar.getmembers():
            file_path = project_dir_name / member.name
            if file_path.is_file() and file_path.exists():
                file_path.unlink()
            tar.extract(member, path=job_dir_name)
            progress.update(task, advance=1)

    printer.print_success(f"[+] Files extracted to {str(project_dir_name).strip()}")
        
def create_job_dirs(job: dict) -> None:
    base_dir = Path(job['server']['base_directory'])
    project_dir = base_dir / job['project']['project_title']
    job_dir = project_dir / job['project_job']['job_directory']
    job_dir.mkdir(parents=True, exist_ok=True)

