import requests
from scientiflow_cli.services.request_handler import make_auth_request
from scientiflow_cli.services.rich_printer import RichPrinter

printer = RichPrinter()

def get_jobs() -> list[dict]:
    response = make_auth_request(endpoint="/agent-application/check-jobs-to-execute", method="GET", error_message="Unable to fetch jobs!")
    try:
        jobs = response.json()
        if len(jobs) == 0:
            printer.print_message("No jobs to execute", style="bold green")
            return []
        else:
            rows = []
            for job in jobs:
                project_job_id: int = job['project_job']['id']
                project_title: str = job['project']['project_title']
                job_title: str = job['project_job']['job_title']
                status: str = job['project_job'].get('status', 'unknown')
                rows.append([str(project_job_id), project_title, job_title, status])

            printer.print_table("Jobs to Execute", columns=[
                {"header": "Project Job ID", "style": "bold cyan", "justify": "center"},
                {"header": "Project Title", "style": "bold white"},
                {"header": "Job Title", "style": "bold yellow"},
                {"header": "Status", "style": "bold green", "justify": "center"}
            ], rows=rows)
            return jobs

    except requests.exceptions.JSONDecodeError:
        printer.print_message("Error fetching jobs - Invalid JSON", style="bold red")
        return []
