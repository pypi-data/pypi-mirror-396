from concurrent.futures import ThreadPoolExecutor
import asyncio
from scientiflow_cli.pipeline.get_jobs import get_jobs
from scientiflow_cli.pipeline.decode_and_execute import decode_and_execute_pipeline, global_bg_tracker
from scientiflow_cli.pipeline.container_manager import get_job_containers
from scientiflow_cli.utils.file_manager import create_job_dirs, get_job_files
from scientiflow_cli.services.rich_printer import RichPrinter

printer = RichPrinter()


def get_all_pending_jobs() -> list[dict]:
    """
    Gets all the pending and running jobs using the get_jobs function
    """
    try:
        return get_jobs()

    except Exception as e:
        printer.print_error("An unexpected error occurred")
        return []


def execute_jobs(job_ids: list[int] = None, parallel: bool = False) -> None:
    """
    Execute jobs based on the provided job IDs. If no job IDs are provided, execute all pending jobs.
    If `parallel` is True, execute jobs asynchronously.
    """
    all_pending_jobs = get_all_pending_jobs()

    if job_ids:
        # Filter jobs based on provided job IDs
        jobs_to_execute = []
        for job_id in job_ids:
            matching_jobs = [job for job in all_pending_jobs if job['project_job']['id'] == job_id]
            if matching_jobs:
                jobs_to_execute.extend(matching_jobs)
            else:
                printer.print_error(f"Job with id: {job_id} not found")
    else:
        # Execute all pending jobs if no IDs are provided
        jobs_to_execute = all_pending_jobs

        # Display all pending jobs
        printer.print_info(f"Executing all pending jobs: {[job['project_job']['id'] for job in jobs_to_execute]}")

    if parallel:
        # Execute jobs asynchronously
        asyncio.run(execute_async(jobs_to_execute))
    else:
        # Execute jobs synchronously
        for job in jobs_to_execute:
            execute_single_job(job)
        
        # Wait for all background jobs from all executed jobs to complete
        global_bg_tracker.wait_for_all_jobs()


def execute_jobs_sync(job_ids: list[int] = None) -> None:
    """
    Execute all jobs synchronously and in order
    """

    all_pending_jobs: list[dict] = []
    all_pending_jobs = get_all_pending_jobs()
    all_pending_jobs = sort_jobs_by_id(all_pending_jobs)

    job_dict: dict[int, dict] = store_jobs_in_dict(all_pending_jobs)

    for job_id in job_ids:
        if job_id not in job_dict:
            printer.print_error(f"No job found with ID: {job_id}")
            continue
        execute_single_job(job_dict[job_id])
    
    # Wait for all background jobs from all executed jobs to complete
    global_bg_tracker.wait_for_all_jobs()


def sort_jobs_by_id(all_pending_jobs: list[dict]) -> list[dict]:
    """
    Sorts all the jobs on basis of the project job id
    """

    all_pending_jobs = sorted(all_pending_jobs, key=lambda job: job['project']['id'])
    return all_pending_jobs


def store_jobs_in_dict(all_pending_jobs: list[dict]) -> dict:
    """
    Stores all the jobs in a dictionary with project job id as key
    """

    job_dict: dict[int, dict] = {}

    for job in all_pending_jobs:
        # checking if the required values are present in the job
        if 'project' not in job or 'id' not in job['project']:
            printer.print_warning("One or more values missing in job. Continuing without considering it.")
            continue
        
        job_dict[job['project_job']['id']] = job

    return job_dict


def execute_job_id(job_id: int) -> None:
    """
    Execute job with the given job_id
    """
    
    # Retrieve all jobs using 'get_jobs'
    all_pending_jobs: list[dict] = []
    
    all_pending_jobs = get_all_pending_jobs()

    # Store jobs in order of their job_id
    job_dict: dict[int, dict] = store_jobs_in_dict(all_pending_jobs)

    if job_id not in job_dict:
        printer.print_error(f"No job found with ID: {job_id}")
        return

    execute_single_job(job_dict[job_id])
    
    # Wait for all background jobs to complete
    global_bg_tracker.wait_for_all_jobs()
    


async def execute_async(jobs: list[dict]) -> None:
    """Execute jobs asynchronously."""
    running_jobs = []

    for job in jobs:
        job_id = job['project_job']['id']
        if job_id not in [j['project_job']['id'] for j in get_all_pending_jobs()]:
            printer.print_error(f"No job found with ID: {job_id}")
            continue

        job_data = execute_single_job_sync(job)

        if job_data is None:
            printer.print_warning(f"[SKIPPING] Job due to an error: {job}")
            continue

        base_dir, project_id, project_job_id, project_title, job_dir_name, nodes, edges, environment_variables, start_node, end_node, job_status, current_node_from_config = job_data

        printer.print_info(f"[ASYNC START] Job {project_job_id} is starting...")

        # Schedule the job asynchronously
        task = asyncio.create_task(
            execute_single_job_async(
                base_dir, project_id, project_job_id, project_title, job_dir_name, nodes, edges, environment_variables, start_node, end_node, job_status, current_node_from_config
            )
        )

        running_jobs.append(task)

    await asyncio.gather(*running_jobs)  # Wait for all jobs to complete
    printer.print_success("[ASYNC COMPLETE] All jobs finished!")
    
    # Wait for all background jobs from all executed jobs to complete
    global_bg_tracker.wait_for_all_jobs()


def execute_single_job(job: dict) -> None:
    """Function to decode and execute a job."""
    try:
        # Validate the job dictionary
        required_keys = ["server", "project", "project_job", "nodes", "edges", "new_job"]

        for key in required_keys:
            if key not in job:
                raise ValueError(f"Job is missing required key: {key}")

        printer.print_success(f"Executing job with id: {job['project_job']['id']}")

        # Store all the variables with their types
        base_dir: str = job['server']['base_directory']
        project_id: int = job['project']['id']
        project_job_id: int = job['project_job']['id']
        project_title: str = job['project']['project_title']
        job_dir_name: str = job['project_job']['job_directory']
        nodes: list[dict] = job['nodes']
        edges: list[dict] = job['edges']
        environment_variables_management: list[dict] = job['environment_variable_management']
        start_node: str = job["project_job"]['job_configuration']['start_node'] if 'job_configuration' in job["project_job"] else None
        end_node: str = job["project_job"]['job_configuration']['end_node'] if 'job_configuration' in job['project_job'] else None
        
        # Extract status and current_node from job configuration
        job_status: str = job['project_job'].get('status')
        current_node_from_config: str = job["project_job"]['job_configuration'].get('current_node') if 'job_configuration' in job["project_job"] else None
        
        if environment_variables_management:
            environment_variables: dict = {environment_var['variable']: environment_var['value'] for environment_var in environment_variables_management}
        else:
            environment_variables = {'variable': 't', 'type': 'text', 'value': '1AKI'}

        # Skip initialization steps if job is already running
        if job_status != "running":
            if job["new_job"] == 1:
                # Initialize folders for the project / project_job 
                create_job_dirs(job)

            # Fetch the files and folder from the backend
            get_job_files(job)

            # Get the job containers from the backend
            get_job_containers(job)

        # Decode and execute the pipeline step by step
        if job_status == "running":
            printer.print_success(f"[+] Resuming execution for job ID: {project_job_id}")
        else:
            printer.print_success(f"[+] Starting execution for job ID: {project_job_id}")
            
        decode_and_execute_pipeline(base_dir, project_id, project_job_id, project_title, job_dir_name, nodes, edges, environment_variables, start_node=start_node, end_node=end_node, job_status=job_status, current_node_from_config=current_node_from_config)
        printer.print_success(f"[+] Execution completed for job ID: {project_job_id}")

    except ValueError as value_err:
        printer.print_error(f"ValueError encountered while processing job: {value_err}")

    except RuntimeError as runtime_err:
        printer.print_error(f"RuntimeError encountered while processing job: {runtime_err}")

    except Exception as err:
        printer.print_error(f"An unexpected error occurred while processing job: {err}")


def execute_single_job_sync(job: dict) -> tuple:
    """Function to decode and execute a job synchronously.
       Processes a job synchronously except for the decode_and_execute_pipeline function.
       
       Raises:
           ValueError: If the job is missing required fields.
           RuntimeError: If the job fails during runtime
    """
    try:
        # Validate the job dictionary
        required_keys = ["server", "project", "project_job", "nodes", "edges", "new_job"]

        for key in required_keys:
            if key not in job:
                raise ValueError(f"Job is missing required key: {key}")

        printer.print_success(f"Executing job with id: {job['project_job']['id']}")

        # Store all the variables with their types
        base_dir: str = job['server']['base_directory']
        project_id: int = job['project']['id']
        project_job_id: int = job['project_job']['id']
        project_title: str = job['project']['project_title']
        job_dir_name: str = job['project_job']['job_directory']
        nodes: list[dict] = job['nodes']
        edges: list[dict] = job['edges']
        environment_variables_management: list[dict] = job['environment_variable_management']
        start_node: str = job["project_job"]['job_configuration']['start_node'] if 'job_configuration' in job["project_job"] else None
        end_node: str = job["project_job"]['job_configuration']['end_node'] if 'job_configuration' in job['project_job'] else None
        
        # Extract status and current_node from job configuration
        job_status: str = job['project_job'].get('status')
        current_node_from_config: str = job["project_job"]['job_configuration'].get('current_node') if 'job_configuration' in job["project_job"] else None
        
        if environment_variables_management:
            environment_variables: dict = {environment_var['variable']: environment_var['value'] for environment_var in environment_variables_management}
        else:
            environment_variables = {'variable': 't', 'type': 'text', 'value': '1AKI'}

        # Skip initialization steps if job is already running
        if job_status != "running":
            if job["new_job"] == 1:
                # Initialize folders for the project / project_job 
                create_job_dirs(job)

            # Fetch the files and folder from the backend
            get_job_files(job)

            # Get the job containers from the backend
            get_job_containers(job)

        return base_dir, project_id, project_job_id, project_title, job_dir_name, nodes, edges, environment_variables, start_node, end_node, job_status, current_node_from_config

    except ValueError as value_err:
        printer.print_error(f"ValueError encountered while processing job: {value_err}")

    except RuntimeError as runtime_err:
        printer.print_error(f"RuntimeError encountered while processing job: {runtime_err}")

    except Exception as err:
        printer.print_error(f"An unexpected error occurred while processing job: {err}")
        return None


async def execute_single_job_async(base_dir, project_id, project_job_id, project_title, job_dir_name, nodes, edges, environment_variables, start_node, end_node, job_status, current_node_from_config) -> None:
    """Function to decode and execute a job asynchronously."""
    try:
        printer.print_info(f"[ASYNC RUNNING] Job {project_job_id} is executing...")

        # Ensure this function runs asynchronously (if it's blocking)
        await asyncio.to_thread(
            decode_and_execute_pipeline,  # Call it as a regular function in a thread
            base_dir, project_id, project_job_id, project_title, job_dir_name, nodes, edges, environment_variables, start_node, end_node, job_status, current_node_from_config
        )

        printer.print_success(f"[ASYNC FINISHED] Job {project_job_id} is done!")

    except Exception as err:
        printer.print_error(f"[ERROR] Job {project_job_id} failed: {err}")
