from scientiflow_cli.services.auth_service import AuthService
from scientiflow_cli.services.rich_printer import RichPrinter
from scientiflow_cli.cli.auth_utils import setAuthToken

def login_user(token: str = None):
    printer = RichPrinter()
    auth_service = AuthService()

    if token:
        # Directly set the token if provided
        setAuthToken(token)
        printer.print_message("Login successful using provided token!", style="bold green")
        return

    email = printer.prompt_input("[bold cyan]Enter your email[/bold cyan]")
    password = printer.prompt_input("[bold cyan]Enter your password[/bold cyan]", password=True)
    result = auth_service.login(email, password)
    if result["success"]:
        printer.print_message(result["message"], style="bold green")
    else:
        printer.print_error(result["message"])