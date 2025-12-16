from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table
from rich.prompt import Prompt
from pwinput import pwinput

class RichPrinter:
    def __init__(self):
        self.console = Console()

    def print_message(self, message: str, style: str = "bold white"):
        """Print a styled message."""
        self.console.print(f"[{style}]{message}[/{style}]")

    def print_error(self, message: str):
        """Print an error message in bold red."""
        self.print_message(message, style="bold red")

    def print_success(self, message: str):
        """Print a success message in bold green."""
        self.print_message(message, style="bold green")

    def print_info(self, message: str):
        """Print an informational message in bold cyan."""
        self.print_message(message, style="bold cyan")

    def print_panel(self, message: str, style: str = "bold white", border_style: str = "white"):
        """Print a message inside a styled panel."""
        self.console.print(Panel(f"{message}", style=style, border_style=border_style))

    def create_progress_bar(self, description: str, total: int):
        """Create a progress bar for tracking tasks."""
        progress = Progress()
        task = progress.add_task(description, total=total)
        return progress, task

    def print_table(self, title: str, columns: list, rows: list):
        """Print a table with the given title, columns, and rows."""
        table = Table(title=title, title_style="bold green")
        for column in columns:
            table.add_column(column["header"], style=column.get("style", "bold white"), justify=column.get("justify", "left"))
        for row in rows:
            table.add_row(*row)
        self.console.print(table)

    def prompt_input(self, message: str, password: bool = False) -> str:
        """Prompt the user for input with an optional password field."""
        if password:
            self.console.print(f"[bold cyan]{message}[/bold cyan]", end="")
            return pwinput(prompt=": ")
        return Prompt.ask(message)