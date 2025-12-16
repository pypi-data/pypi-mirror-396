import os
from scientiflow_cli.services.auth_service import AuthService
from scientiflow_cli.services.rich_printer import RichPrinter

def logout_user():
    printer = RichPrinter()
    auth_service = AuthService()
    result = auth_service.logout()
    if result["success"]:
        printer.print_message(result["message"], style="bold green")
    else:
        printer.print_panel(result["message"], style="bold red")
