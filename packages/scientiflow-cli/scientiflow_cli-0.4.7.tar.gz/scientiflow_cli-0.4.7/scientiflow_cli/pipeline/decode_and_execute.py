import subprocess
import tempfile
import os
import re, shlex
import multiprocessing
import threading
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, List, Any
from scientiflow_cli.services.status_updater import update_job_status, update_stopped_at_node, update_current_node, get_job_status, get_current_node
from scientiflow_cli.services.request_handler import make_auth_request
from scientiflow_cli.services.rich_printer import RichPrinter

printer = RichPrinter()

# Global background job tracker
class GlobalBackgroundJobTracker:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.background_executors = []
        self.background_jobs_count = 0
        self.background_jobs_completed = 0
        self.background_jobs_lock = threading.Lock()
    
    def register_background_job(self, executor, futures, node_label, log_file_path):
        """Register a background job for global tracking."""
        with self.background_jobs_lock:
            self.background_jobs_count += 1
            self.background_executors.append(executor)
        
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(
            target=self._monitor_job,
            args=(futures, node_label, executor, log_file_path),
            daemon=True
        )
        monitor_thread.start()
    
    def _monitor_job(self, futures, node_label, executor, log_file_path):
        """Monitor background job completion."""
        all_successful = True
        for future in as_completed(futures):
            success = future.result()
            if not success:
                all_successful = False
        
        if not all_successful:
            with open(log_file_path, 'a') as f:
                f.write(f"[ERROR] Background job {node_label} failed\n")
            printer.print_message(f"[BACKGROUND JOB] {node_label} Failed - some commands in background job failed", style="bold red")
        else:
            printer.print_message(f"[BACKGROUND JOB] {node_label} Execution completed in the background", style="bold green")
        
        # Clean up executor
        executor.shutdown(wait=False)
        with self.background_jobs_lock:
            if executor in self.background_executors:
                self.background_executors.remove(executor)
            self.background_jobs_completed += 1
    
    def wait_for_all_jobs(self):
        """Wait for all background jobs to complete."""
        import time
        if self.background_jobs_count > 0:
            printer.print_message(f"[INFO] Waiting for {self.background_jobs_count} background job(s) to complete...", style="bold yellow")
            
            while True:
                with self.background_jobs_lock:
                    if self.background_jobs_completed >= self.background_jobs_count:
                        break
                time.sleep(0.5)  # Check every 500ms
            
            printer.print_message("[INFO] All background jobs completed.", style="bold green")
    
    def reset(self):
        """Reset the tracker for a new execution cycle."""
        with self.background_jobs_lock:
            self.background_executors = []
            self.background_jobs_count = 0
            self.background_jobs_completed = 0

# Global tracker instance
global_bg_tracker = GlobalBackgroundJobTracker()

def execute_background_command_standalone(command: str, log_file_path: str):
    """Execute a command in background without real-time output display - standalone function for multiprocessing."""
    try:
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, _ = proc.communicate()
        
        result = output.decode(errors="replace")
        
        # Log the output to the specific log file
        with open(log_file_path, 'a') as f:
            f.write(result + "\n")
        
        if proc.returncode != 0:
            with open(log_file_path, 'a') as f:
                f.write(f"[ERROR] Command failed with return code {proc.returncode}\n")
            return False
        
        return True
        
    except Exception as e:
        with open(log_file_path, 'a') as f:
            f.write(f"[ERROR] An unexpected error occurred: {e}\n")
        return False

class PipelineExecutor:
    def __init__(self, base_dir: str, project_id: int, project_job_id: int, project_title: str, job_dir_name: str, nodes: List[Dict[str, Any]], edges: List[Dict[str, str]], environment_variables: Dict[str, str], start_node: str = None, end_node: str = None, job_status: str = None, current_node_from_config: str = None):
        self.base_dir = base_dir
        self.project_id = project_id
        self.project_job_id = project_job_id
        self.project_title = project_title
        self.job_dir_name = job_dir_name
        self.nodes = nodes
        self.edges = edges
        self.environment_variables = environment_variables
        self.start_node = start_node
        self.end_node = end_node
        self.current_node = None
        self.job_status = job_status
        self.current_node_from_config = current_node_from_config
        
        # For resuming: flag to track if we've reached the resume point
        self.resume_mode = (job_status == "running" and current_node_from_config is not None)
        self.reached_resume_point = False

        # Set up job-specific log file
        self.log_file_path = os.path.join(self.base_dir, self.project_title, self.job_dir_name, "logs", "output.log")
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)

        # Create mappings for efficient execution
        self.nodes_map = {node['id']: node for node in nodes}
        self.adj_list = {node['id']: [] for node in nodes}
        for edge in edges:
            self.adj_list[edge['source']].append(edge['target'])

        # Identify root nodes (nodes with no incoming edges)
        all_nodes = set(self.nodes_map.keys())
        target_nodes = {edge['target'] for edge in edges}
        self.root_nodes = all_nodes - target_nodes

        # Initialize log file
        self.init_log()

    def init_log(self):
        """Initialize the log file."""
        try:
            # If job is running (resuming), append to existing log file
            # Otherwise, create a fresh log file
            if self.job_status == "running":
                # Check if log file exists, if not create it
                with open(self.log_file_path, 'a') as f:
                    f.write('')
            else:
                # Create fresh log file for new execution
                with open(self.log_file_path, 'w') as f:
                    f.write('')
        except Exception as e:
            print(f"[ERROR] Failed to initialize log file: {e}")

    def log_output(self, text: str):
        """Write to log file."""
        try:
            with open(self.log_file_path, 'a') as f:
                f.write(text + "\n")
        except Exception as e:
            print(f"[ERROR] Failed to write log: {e}")

    def update_terminal_output(self):
        """Update the terminal output after execution is complete."""
        try:
            with open(self.log_file_path, 'r') as f:
                terminal_output = f.read()
            body = {"project_job_id": self.project_job_id, "terminal_output": terminal_output}
            make_auth_request(endpoint="/agent-application/update-terminal-output", method="POST", data=body, error_message="Unable to update terminal output!")
            printer.print_message("[+] Terminal output updated successfully.", style="bold green")
        except Exception as e:
            print(f"[ERROR] Failed to update terminal output: {e}")

    def replace_variables(self, command: str) -> str:
        #     """Replace placeholders like ${VAR} with environment values."""
        #     print(self.environment_variables)
        #     return re.sub(r'\$\{(\w+)\}', lambda m: self.environment_variables.get(m.group(1), m.group(0)), command)
        """Replace placeholders like ${VAR} with environment values.
        - If value is a list: safely join into space-separated arguments (quoted).
        - Otherwise: use the old behavior (direct substitution).
        """
        def replacer(match):
            key = match.group(1)
            value = self.environment_variables.get(key, match.group(0))
            # ✅ Special handling for lists
            if isinstance(value, list):
                return " ".join(shlex.quote(str(v)) for v in value)
            # ✅ Default: keep original behavior for strings, numbers, None
            return self.environment_variables.get(key, match.group(0))
        return re.sub(r'\$\{(\w+)\}', replacer, command)
        
    def execute_command(self, command: str):
        """Run the command in the terminal, display output in real-time, and log the captured output."""
        import sys
        try:
            with tempfile.TemporaryFile() as tempf:
                proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                while True:
                    chunk = proc.stdout.read(1)
                    if not chunk:
                        break
                    sys.stdout.buffer.write(chunk)
                    sys.stdout.flush()
                    tempf.write(chunk)
                proc.stdout.close()
                proc.wait()

                tempf.seek(0)
                result = tempf.read().decode(errors="replace")
                self.log_output(result)  # Log the entire output

                if proc.returncode != 0:
                    self.log_output(f"[ERROR] Command failed with return code {proc.returncode}")
                    update_job_status(self.project_job_id, "failed")
                    update_stopped_at_node(self.project_id, self.project_job_id, self.current_node)
                    self.update_terminal_output()
                    raise SystemExit("[ERROR] Pipeline execution terminated due to failure.")

        except Exception as e:
            self.log_output(f"[ERROR] An unexpected error occurred: {e}")
            update_job_status(self.project_job_id, "failed")
            update_stopped_at_node(self.project_id, self.project_job_id, self.current_node)
            self.update_terminal_output()
            raise SystemExit("[ERROR] Pipeline execution terminated due to an unexpected error.")



    def dfs(self, node: str):
        """Perform Depth-First Search (DFS) for executing pipeline nodes."""
        if self.current_node == self.end_node:
            return

        self.current_node = node
        current_node = self.nodes_map[node]
        
        # Check if we've reached the resume point
        if self.resume_mode and not self.reached_resume_point:
            if node == self.current_node_from_config:
                self.reached_resume_point = True
                node_label = current_node['data'].get('label', node)
                printer.print_message(f"[INFO] Reached resume point: {node_label} - continuing execution", style="bold green")
            else:
                # Skip execution for this node, just traverse
                if current_node['type'] == "splitterParent":
                    collector = None
                    for child in self.adj_list[node]:
                        if self.nodes_map[child]['data']['active']:
                            collector = self.dfs(child)
                    if collector and self.adj_list[collector]:
                        return self.dfs(self.adj_list[collector][0])
                    return
                elif current_node['type'] == "splitter-child":
                    if current_node['data']['active'] and self.adj_list[node]:
                        return self.dfs(self.adj_list[node][0])
                    return
                elif current_node['type'] == "terminal":
                    if self.adj_list[node]:
                        return self.dfs(self.adj_list[node][0])
                    return
                elif current_node['type'] == "collector":
                    return node if self.adj_list[node] else None

        # Normal execution (either not in resume mode or already reached resume point)
        if current_node['type'] == "splitterParent":
            collector = None
            for child in self.adj_list[node]:
                if self.nodes_map[child]['data']['active']:
                    collector = self.dfs(child)
            if collector and self.adj_list[collector]:
                return self.dfs(self.adj_list[collector][0])
            return

        elif current_node['type'] == "splitter-child":
            if current_node['data']['active'] and self.adj_list[node]:
                return self.dfs(self.adj_list[node][0])
            return

        elif current_node['type'] == "terminal":
            # Update current node status
            update_current_node(self.project_id, self.project_job_id, node)
            
            commands = current_node['data']['commands']
            isGPUEnabled = current_node['data'].get('gpuEnabled', False)
            isBackgroundNode = current_node['data'].get('executeInBackground', False)
            node_label = current_node['data'].get('label', 'Unknown Node')
            
            if isBackgroundNode:
                # Background execution with multiprocessing
                numberOfThreads = current_node['data'].get('numberOfThreads', 1)
                printer.print_message(f"[BACKGROUND JOB] {node_label} Execution started in background", style="bold blue")
                
                # Prepare commands for parallel execution
                command_list = []
                for command in commands:
                    cmd = self.replace_variables(command.get('command', ''))
                    if cmd:
                        base_command = f"cd {self.base_dir}/{self.project_title}/{self.job_dir_name} && singularity exec "
                        container_path = f"{self.base_dir}/containers/{current_node['data']['software']}.sif"
                        gpu_flag = "--nv --nvccli" if isGPUEnabled else ""
                        full_command = f"{base_command} {gpu_flag} {container_path} {cmd}"
                        command_list.append(full_command)
                
                # Execute commands in background using ProcessPoolExecutor (non-blocking)
                if command_list:
                    executor = ProcessPoolExecutor(max_workers=numberOfThreads)
                    futures = []
                    for cmd in command_list:
                        future = executor.submit(execute_background_command_standalone, cmd, self.log_file_path)
                        futures.append(future)
                    
                    # Register with global tracker (non-blocking)
                    global_bg_tracker.register_background_job(executor, futures, node_label, self.log_file_path)
                    
                    # Don't wait for completion, immediately continue to next node
                else:
                    printer.print_message(f"[BACKGROUND JOB] {node_label} No commands to execute", style="bold yellow")
            else:
                # Normal execution with real-time output
                for command in commands:
                    cmd = self.replace_variables(command.get('command', ''))
                    if cmd:
                        base_command = f"cd {self.base_dir}/{self.project_title}/{self.job_dir_name} && singularity exec "
                        container_path = f"{self.base_dir}/containers/{current_node['data']['software']}.sif"
                        gpu_flag = "--nv --nvccli" if isGPUEnabled else ""
                        full_command = f"{base_command} {gpu_flag} {container_path} {cmd}"
                        self.execute_command(full_command)

            if self.adj_list[node]:
                return self.dfs(self.adj_list[node][0])
            return

        elif current_node['type'] == "collector":
            return node if self.adj_list[node] else None

    def decode_and_execute_pipeline(self):
        """Start executing the pipeline."""
        # Use job status from configuration instead of API call
        current_status = self.job_status
        
        if current_status == "running":
            # Job is already running, resume from start but skip until current node
            current_node_id = self.current_node_from_config
            if current_node_id and current_node_id in self.nodes_map:
                # Get the label from the current node
                current_node_label = self.nodes_map[current_node_id]['data'].get('label', current_node_id)
                printer.print_message(f"[INFO] Resuming job - will skip to node: {current_node_label}", style="bold blue")
                # Start from the beginning (start_node or root)
                starting_node = self.start_node or next(iter(self.root_nodes), None)
            else:
                printer.print_message("[WARNING] Current node not found, starting from beginning", style="bold yellow")
                starting_node = self.start_node or next(iter(self.root_nodes), None)
        else:
            # Job is not running, start normally
            update_job_status(self.project_job_id, "running")
            starting_node = self.start_node or next(iter(self.root_nodes), None)

        if starting_node:
            self.dfs(starting_node)

        # Don't wait for background jobs here - let them continue across multiple jobs
        # Background jobs will be waited for at the end of all job executions
        
        update_job_status(self.project_job_id, "completed")
        update_stopped_at_node(self.project_id, self.project_job_id, self.current_node)

        # Update terminal output at the end of execution
        self.update_terminal_output()

# External function to initiate the pipeline execution
def decode_and_execute_pipeline(base_dir: str, project_id: int, project_job_id: int, project_title: str, job_dir_name: str, nodes: List[Dict[str, Any]], edges: List[Dict[str, str]], environment_variables: Dict[str, str], start_node: str = None, end_node: str = None, job_status: str = None, current_node_from_config: str = None):
    """Initialize and execute the pipeline."""
    executor = PipelineExecutor(base_dir, project_id, project_job_id, project_title, job_dir_name, nodes, edges, environment_variables, start_node, end_node, job_status, current_node_from_config)
    executor.decode_and_execute_pipeline()