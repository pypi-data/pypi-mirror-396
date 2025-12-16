import argparse
import sys
import pathlib
import re
from importlib import metadata as importlib_metadata
from importlib.metadata import PackageNotFoundError
from scientiflow_cli.cli.login import login_user
from scientiflow_cli.cli.logout import logout_user
from scientiflow_cli.pipeline.get_jobs import get_jobs
from scientiflow_cli.services.executor import execute_jobs, execute_jobs_sync, execute_job_id
from scientiflow_cli.services.base_directory import set_base_directory, get_base_directory
from scientiflow_cli.utils.singularity import install_singularity_main as install_singularity
from scientiflow_cli.pipeline.container_manager import manage_containers
from scientiflow_cli.services.rich_printer import RichPrinter
from art import text2art

printer = RichPrinter()

class RichArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        printer.print_message(f"Error: {message}", style="bold red")
        self.print_help()
        sys.exit(2)

def display_title():
    title_art = text2art("ScientiFlow")
    printer.print_message(title_art, style="bold blue")

def display_help(parser):
    columns = [
        {"header": "Option", "style": "bold cyan", "justify": "left"},
        {"header": "Description", "style": "bold white", "justify": "left"}
    ]
    rows = []
    for action in parser._actions:
        if action.option_strings and action.help != argparse.SUPPRESS:  # Exclude suppressed arguments
            options = ", ".join(action.option_strings)
            description = action.help if action.help else ""
            rows.append([options, description])
            rows.append(["", ""])  # Add a blank line for spacing

    printer.print_table("Scientiflow Agent CLI", columns, rows)


def get_package_version() -> str:
    """Return the package version.

    Try to get the installed package version via importlib.metadata. If the
    package isn't installed (PackageNotFoundError), fall back to reading the
    `pyproject.toml` file in the project root.
    """
    try:
        return importlib_metadata.version("scientiflow-cli")
    except PackageNotFoundError:
        try:
            # Project root is two levels up from this file: .../scientiflow_cli/main.py
            project_root = pathlib.Path(__file__).resolve().parents[1]
            pyproject = project_root / "pyproject.toml"
            if pyproject.exists():
                text = pyproject.read_text(encoding="utf-8")
                m = re.search(r"^version\s*=\s*[\"']([^\"']+)[\"']", text, re.MULTILINE)
                if m:
                    return m.group(1)
        except Exception:
            pass
    return "unknown"

def main():
    parser = RichArgumentParser(description="Scientiflow Agent CLI", add_help=False)
    parser.formatter_class = lambda prog: argparse.HelpFormatter(prog, max_help_position=50)

    parser.add_argument('-h', '--help', action='store_true', help="Show this help message and exit")
    parser.add_argument('--login', action='store_true', help="Login using your scientiflow credentials")
    parser.add_argument('--logout', action='store_true', help="Logout from scientiflow")
    parser.add_argument('-v', '--version', action='store_true', help="Show package version and exit")
    parser.add_argument('--list-jobs', action='store_true', help="Get all the pending jobs to execute")
    parser.add_argument('--set-base-directory', action='store_true', help="Set the base directory to the current working directory \nOptionally, use --hostname to specify the hostname for this server")
    parser.add_argument('-p', '--parallel', action='store_true', help=argparse.SUPPRESS)  # Hide -p or --parallel from --help
    parser.add_argument('--install-singularity', action='store_true', help="Install Singularity \nOptionally, use --enable-gpu to enable GPU support during installation")
    parser.add_argument('--enable-gpu', action='store_true', help=argparse.SUPPRESS)  # Hide --enable-gpu from --help
    parser.add_argument('--manage-containers', action='store_true', help="Manage containers at the already set base directory")
    parser.add_argument('--execute-jobs', nargs='*', type=int, help="Execute jobs. Specify job IDs as arguments \n(e.g., --execute-jobs jobID1 jobID2 ...) or leave empty to execute all jobs.\nUse -p or --parallel flag to execute jobs in parallel.")
    parser.add_argument('--hostname', type=str, help=argparse.SUPPRESS)  # Hide --hostname from --help
    parser.add_argument('--token', type=str, help=argparse.SUPPRESS)  # Hide --token from --help

    # Parse arguments
    args, unknown_args = parser.parse_known_args()

    # Handle -p or --parallel explicitly
    args.parallel = args.parallel or ('-p' in unknown_args or '--parallel' in unknown_args)

    # Remove -p or --parallel from unknown_args to avoid parsing issues
    if '-p' in unknown_args:
        unknown_args.remove('-p')
    if '--parallel' in unknown_args:
        unknown_args.remove('--parallel')

    # Re-parse arguments with cleaned-up unknown_args
    args = parser.parse_args(unknown_args, namespace=args)

    if args.help:
        display_title()
        display_help(parser)
        sys.exit()

    if args.version:
        version = get_package_version()
        printer.print_message(f"Version: {version}", style="bold green")
        sys.exit()

    try:
        if args.login:
            login_user(token=args.token)
        elif args.logout:
            logout_user()
        elif args.list_jobs:
            get_jobs()
        elif args.set_base_directory:
            set_base_directory(hostname=args.hostname)
        elif args.execute_jobs is not None:
            # Use the parsed `parallel` flag
            job_ids = args.execute_jobs if args.execute_jobs else None
            execute_jobs(job_ids=job_ids, parallel=args.parallel)
        elif args.install_singularity:
            install_singularity(enable_gpu=args.enable_gpu)
        elif args.manage_containers:
            base_dir = get_base_directory()
            if not base_dir:
                sys.exit(2)
            manage_containers(base_dir=base_dir)
        else:
            display_title()
            printer.print_message("No arguments specified. Use --help to see available options", style="bold red")

    except KeyboardInterrupt:
        printer.print_message("\n\n[~] Execution interrupted by user. Exiting gracefully.", style="bold yellow")
        sys.exit(0)
    except Exception as e:
        printer.print_panel(f"Error: {e}", style="bold red")
        return

    sys.exit()

if __name__ == "__main__":
    main()