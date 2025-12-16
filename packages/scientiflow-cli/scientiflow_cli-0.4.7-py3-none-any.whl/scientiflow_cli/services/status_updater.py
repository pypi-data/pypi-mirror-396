from scientiflow_cli.services.request_handler import make_auth_request
from scientiflow_cli.services.rich_printer import RichPrinter

printer = RichPrinter()

def update_stopped_at_node(project_id: int, project_job_id: int, stopped_at_node: str):
    body = {"project_id": project_id, "project_job_id": project_job_id, "stopped_at_node": stopped_at_node}
    try:
        make_auth_request(endpoint="/jobs/update-stopped-at-node", method="POST", data=body, error_message="Unable to update stopped at node!")
        printer.print_message("[+] Stopped at node updated successfully.", style="bold green")
    except Exception as e:
        printer.print_panel(f"Error updating stopped at node: {e}", style="bold red")

def update_current_node(project_id: int, project_job_id: int, current_node: str):
    body = {"project_id": project_id, "project_job_id": project_job_id, "current_node": current_node}
    try:
        make_auth_request(endpoint="/jobs/update-current-node", method="POST", data=body, error_message="Unable to update current node!")
    except Exception as e:
        printer.print_panel(f"Error updating current node: {e}", style="bold red")

def update_job_status(project_job_id: int, status: str):
    body = {"project_job_id": project_job_id, "status": status}
    try:
        make_auth_request(endpoint="/agent-application/update-project-job-status", method="POST", data=body, error_message="Unable to update job status!")
        printer.print_message("[+] Project status updated successfully.", style="bold green")
    except Exception as e:
        printer.print_panel(f"Error updating job status: {e}", style="bold red")

def get_job_status(project_job_id: int):
    """Get the current status of a job."""
    try:
        response = make_auth_request(endpoint=f"/jobs/get-job-status/{project_job_id}", method="GET", error_message="Unable to get job status!")
        if response.status_code == 200:
            data = response.json()
            return data.get('status')
        else:
            printer.print_panel(f"Error getting job status: HTTP {response.status_code}", style="bold red")
            return None
    except Exception as e:
        printer.print_panel(f"Error getting job status: {e}", style="bold red")
        return None

def get_current_node(project_job_id: int):
    """Get the current node of a job."""
    try:
        response = make_auth_request(endpoint=f"/jobs/get-current-node/{project_job_id}", method="GET", error_message="Unable to get current node!")
        if response.status_code == 200:
            data = response.json()
            return data.get('current_node')
        else:
            printer.print_panel(f"Error getting current node: HTTP {response.status_code}", style="bold red")
            return None
    except Exception as e:
        printer.print_panel(f"Error getting current node: {e}", style="bold red")
        return None
