"""Command-line interface for clserve."""

import logging
from typing import Optional
import click
from prettytable import PrettyTable

from clserve import __version__
from clserve.submit import SubmitArgs, serve
from clserve.status import (
    list_serving_jobs,
    get_job_info,
    find_jobs_by_model,
    JobInfo,
    CLSERVE_LOGS_DIR,
)
from clserve.stop import stop_by_job_id, stop_all
from clserve.configs import list_available_configs, load_model_config


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
    )


def select_job(jobs: list[JobInfo], action: str = "select") -> Optional[JobInfo]:
    """Prompt user to select a job from a list.

    Args:
        jobs: List of jobs to choose from
        action: Description of the action (for prompt text)

    Returns:
        Selected job or None if cancelled
    """
    if not jobs:
        return None

    if len(jobs) == 1:
        return jobs[0]

    # Multiple jobs - show selector
    click.echo(f"Multiple jobs found. Select one to {action}:")
    click.echo()

    for i, job in enumerate(jobs, 1):
        model_name = ""
        if job.model_path:
            model_name = (
                job.model_path.split("/")[-1]
                if "/" in job.model_path
                else job.model_path
            )
        state_icon = "●" if job.state == "RUNNING" else "○"
        url_info = f" - {job.endpoint_url}" if job.endpoint_url else ""
        click.echo(f"  [{i}] {state_icon} {job.job_id}: {model_name}{url_info}")

    click.echo(f"  [0] Cancel")
    click.echo()

    while True:
        choice = click.prompt("Enter number", type=int, default=1)
        if choice == 0:
            return None
        if 1 <= choice <= len(jobs):
            return jobs[choice - 1]
        click.echo(f"Invalid choice. Please enter 0-{len(jobs)}")


@click.group()
@click.version_option(version=__version__)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
def main(verbose: bool):
    """clserve - CLI tool for serving LLM models on Alps.

    Quick start:

      # Serve a model using predefined config
      clserve serve deepseek-v3

      # Check status and get URL
      clserve status

      # Get URL for a specific model
      clserve url deepseek-v3

      # Stop a serving job
      clserve stop deepseek-v3
    """
    setup_logging(verbose)


@main.command()
@click.argument("model")
@click.option("--workers", "-w", type=int, default=1, help="Number of workers")
@click.option("--nodes-per-worker", "-n", type=int, default=1, help="Nodes per worker")
@click.option("--partition", "-p", type=str, default="normal", help="SLURM partition")
@click.option(
    "--environment",
    "-e",
    type=str,
    default="sglang_gb200",
    help="Container environment",
)
@click.option("--tp-size", type=int, default=1, help="Tensor parallel size")
@click.option("--dp-size", type=int, default=1, help="Data parallel size")
@click.option("--ep-size", type=int, default=1, help="Expert parallel size")
@click.option(
    "--num-gpus-per-worker",
    type=click.Choice(["1", "2", "4"]),
    default="4",
    help="GPUs per worker process",
)
@click.option(
    "--cuda-graph-max-bs", type=int, default=256, help="Max batch size for CUDA graphs"
)
@click.option(
    "--grammar-backend", type=str, default="llguidance", help="Grammar backend"
)
@click.option(
    "--use-router/--no-router", default=False, help="Enable load balancer router"
)
@click.option("--router-policy", type=str, default="cache_aware", help="Router policy")
@click.option(
    "--router-environment",
    type=str,
    default="sglang_router",
    help="Router container environment",
)
@click.option(
    "--reasoning-parser", type=str, default="", help="Reasoning parser module"
)
@click.option(
    "--time-limit", "-t", type=str, default="04:00:00", help="Job time limit (HH:MM:SS)"
)
@click.option("--job-name", "-j", type=str, default=None, help="Custom job name")
def serve_cmd(
    model: str,
    workers: int,
    nodes_per_worker: int,
    partition: str,
    environment: str,
    tp_size: int,
    dp_size: int,
    ep_size: int,
    num_gpus_per_worker: str,
    cuda_graph_max_bs: int,
    grammar_backend: str,
    use_router: bool,
    router_policy: str,
    router_environment: str,
    reasoning_parser: str,
    time_limit: str,
    job_name: str,
):
    """Start serving a model.

    MODEL can be:
    - A model alias (e.g., deepseek-v3, llama-405b, qwen3-235b)
    - A HuggingFace model path (e.g., meta-llama/Llama-3.1-70B-Instruct)

    If a predefined configuration exists for the model, it will be used
    as defaults. You can override any setting with command-line options.

    Examples:

      # Serve DeepSeek V3 with predefined config (4 nodes, TP=16)
      clserve serve deepseek-v3

      # Serve with multiple workers
      clserve serve deepseek-v3 --workers 2 --use-router

      # Serve a custom model
      clserve serve my-org/my-model --tp-size 4 --nodes-per-worker 1

      # Serve a small model with 4 instances per node
      clserve serve llama-8b --num-gpus-per-worker 1 --use-router
    """
    args = SubmitArgs(
        model=model,
        workers=workers,
        nodes_per_worker=nodes_per_worker,
        partition=partition,
        environment=environment,
        tp_size=tp_size,
        dp_size=dp_size,
        ep_size=ep_size,
        num_gpus_per_worker=int(num_gpus_per_worker),
        cuda_graph_max_bs=cuda_graph_max_bs,
        grammar_backend=grammar_backend,
        use_router=use_router,
        router_policy=router_policy,
        router_environment=router_environment,
        reasoning_parser=reasoning_parser,
        time_limit=time_limit,
        job_name=job_name,
    )

    # Show config info if using predefined config
    config = load_model_config(model)
    if config:
        click.echo(f"Using predefined config for {model}:")
        click.echo(f"  Model: {config.model_path}")
        click.echo(f"  TP size: {config.tp_size}, DP size: {config.dp_size}")
        click.echo(f"  Nodes per worker: {config.nodes_per_worker}")
        click.echo(f"  GPUs per worker: {config.num_gpus_per_worker}")
        if config.use_router:
            click.echo(f"  Router: enabled ({config.router_policy})")
        click.echo()

    try:
        job_id = serve(args)
        click.echo(f"Job submitted successfully!")
        click.echo(f"  Job ID: {job_id}")
        click.echo(f"  Logs: {CLSERVE_LOGS_DIR / job_id}/log.out")
        click.echo()
        click.echo("Check status with:")
        click.echo(f"  clserve status")
        click.echo()
        click.echo("Get endpoint URL with:")
        click.echo(f"  clserve url {model}")
        click.echo()
        click.echo("Stop the job with:")
        click.echo(f"  clserve stop {model}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


# Alias 'serve' command
main.add_command(serve_cmd, name="serve")


@main.command()
@click.argument("identifier", required=False)
def status(identifier: str = None):
    """Show status of serving jobs.

    IDENTIFIER is optional - can be a job ID or model name.
    If not provided, shows all running jobs.

    Examples:

      # Show all running jobs
      clserve status

      # Show status for a specific job
      clserve status 12345

      # Show status for jobs serving a model
      clserve status deepseek-v3
    """
    if identifier:
        # Show specific job(s)
        if identifier.isdigit():
            job = get_job_info(identifier)
            if job:
                _print_job_details(job)
            else:
                click.echo(f"Job {identifier} not found")
        else:
            jobs = find_jobs_by_model(identifier)
            if jobs:
                _print_jobs_table(jobs)
            else:
                click.echo(f"No jobs found for model '{identifier}'")
    else:
        # Show all jobs
        jobs = list_serving_jobs()
        if jobs:
            _print_jobs_table(jobs)
        else:
            click.echo("No running jobs found")
            click.echo()
            click.echo("Start a new job with:")
            click.echo("  clserve serve <model>")


def _print_job_details(job):
    """Print detailed info for a single job."""
    click.echo(f"Job ID: {job.job_id}")
    click.echo(f"Name: {job.job_name}")
    click.echo(f"State: {job.state}")
    click.echo(f"Nodes: {job.node_list}")
    if job.model_path:
        click.echo(f"Model: {job.model_path}")
    if job.endpoint_url:
        click.echo(f"Endpoint URL: {job.endpoint_url}")
    if job.workers:
        click.echo(f"Workers: {job.workers}")
    if job.nodes_per_worker:
        click.echo(f"Nodes per worker: {job.nodes_per_worker}")
    if job.tp_size:
        click.echo(f"TP size: {job.tp_size}")
    if job.use_router is not None:
        click.echo(f"Router: {'enabled' if job.use_router else 'disabled'}")


def _print_jobs_table(jobs):
    """Print jobs as a table."""
    table = PrettyTable()
    table.field_names = ["Job ID", "Name", "State", "Model", "Endpoint URL"]
    table.align = "l"

    for job in jobs:
        model_name = ""
        if job.model_path:
            model_name = (
                job.model_path.split("/")[-1]
                if "/" in job.model_path
                else job.model_path
            )
            if len(model_name) > 30:
                model_name = model_name[:27] + "..."

        endpoint = job.endpoint_url or "(pending)"
        if len(endpoint) > 35:
            endpoint = endpoint[:32] + "..."

        table.add_row(
            [
                job.job_id,
                job.job_name,
                job.state,
                model_name,
                endpoint,
            ]
        )

    click.echo(table)


@main.command()
@click.argument("model")
def url(model: str):
    """Get the endpoint URL for a serving job.

    MODEL is the model name or alias (e.g., deepseek-v3, llama-405b).
    If multiple jobs are serving the same model, you'll be prompted to select one.

    Examples:

      # Get URL by model name
      clserve url deepseek-v3

      # Get URL by full model path
      clserve url deepseek-ai/DeepSeek-V3.1
    """
    jobs = find_jobs_by_model(model)
    if not jobs:
        click.echo(f"No jobs found for model '{model}'", err=True)
        raise SystemExit(1)

    # Filter to running jobs with URLs first
    running_with_url = [j for j in jobs if j.state == "RUNNING" and j.endpoint_url]
    if len(running_with_url) == 1:
        click.echo(running_with_url[0].endpoint_url)
        return

    # If multiple running jobs or none with URL, use selector
    running_jobs = [j for j in jobs if j.state == "RUNNING"]
    if not running_jobs:
        click.echo(f"No running jobs found for model '{model}'", err=True)
        raise SystemExit(1)

    job = select_job(running_jobs, action="get URL")
    if job is None:
        return  # User cancelled

    if job.endpoint_url:
        click.echo(job.endpoint_url)
    else:
        click.echo(f"Job {job.job_id} does not have an endpoint URL yet", err=True)
        click.echo("The job may still be starting up. Check status with:", err=True)
        click.echo(f"  clserve status", err=True)
        raise SystemExit(1)


@main.command()
@click.argument("model", required=False)
@click.option(
    "--all", "-a", "stop_all_flag", is_flag=True, help="Stop all matching jobs"
)
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
def stop_cmd(model: str = None, stop_all_flag: bool = False, force: bool = False):
    """Stop serving jobs.

    MODEL is the model name or alias (e.g., deepseek-v3, llama-405b).
    If multiple jobs are serving the same model, you'll be prompted to select one
    (unless --all is used).

    Examples:

      # Stop by model name (selector if multiple)
      clserve stop deepseek-v3

      # Stop all jobs for a model
      clserve stop deepseek-v3 --all

      # Stop all running jobs
      clserve stop --all
    """
    if model is None and not stop_all_flag:
        click.echo(
            "Error: Please provide a model name, or use --all to stop all jobs",
            err=True,
        )
        raise SystemExit(1)

    if stop_all_flag and model is None:
        # Stop all clserve jobs
        jobs = list_serving_jobs()
        running = [j for j in jobs if j.state in ["RUNNING", "PENDING"]]
        if not running:
            click.echo("No running jobs to stop")
            return

        if not force:
            click.echo(f"This will stop {len(running)} job(s):")
            for job in running:
                model_name = job.model_path or job.job_name
                if "/" in model_name:
                    model_name = model_name.split("/")[-1]
                click.echo(f"  {job.job_id}: {model_name}")
            if not click.confirm("Continue?"):
                return

        stopped = stop_all()
        if stopped:
            click.echo(f"Stopped {len(stopped)} job(s): {', '.join(stopped)}")
        else:
            click.echo("No jobs were stopped")
    else:
        # Stop job(s) for specific model
        jobs = find_jobs_by_model(model)
        running = [j for j in jobs if j.state in ["RUNNING", "PENDING"]]

        if not running:
            click.echo(f"No running jobs found for model '{model}'", err=True)
            raise SystemExit(1)

        if stop_all_flag:
            # Stop all matching jobs
            if not force:
                click.echo(f"This will stop {len(running)} job(s) for '{model}':")
                for job in running:
                    click.echo(f"  {job.job_id}")
                if not click.confirm("Continue?"):
                    return

            stopped = []
            for job in running:
                if stop_by_job_id(job.job_id):
                    stopped.append(job.job_id)

            if stopped:
                click.echo(f"Stopped {len(stopped)} job(s): {', '.join(stopped)}")
            else:
                click.echo("No jobs were stopped")
        else:
            # Select single job to stop
            job = select_job(running, action="stop")
            if job is None:
                return  # User cancelled

            if stop_by_job_id(job.job_id):
                click.echo(f"Stopped job {job.job_id}")
            else:
                click.echo(f"Failed to stop job {job.job_id}", err=True)
                raise SystemExit(1)


# Alias 'stop' command
main.add_command(stop_cmd, name="stop")


@main.command()
def models():
    """List available predefined model configurations.

    These models have optimized configurations for the cluster.
    Use the alias or full path with 'clserve serve'.

    Example:

      clserve serve deepseek-v3
      clserve serve Qwen/Qwen3-235B-A22B-Instruct-2507
    """
    table = PrettyTable()
    table.field_names = ["Alias", "Model Path", "TP", "Nodes/Worker", "Description"]
    table.align = "l"

    configs = list_available_configs()

    for config_name in sorted(configs):
        # Convert config filename to alias
        alias = config_name.replace("_", "-")
        config = load_model_config(alias)
        if config:
            # Truncate description
            desc = config.description
            if len(desc) > 40:
                desc = desc[:37] + "..."

            table.add_row(
                [
                    alias,
                    config.model_path,
                    config.tp_size,
                    config.nodes_per_worker,
                    desc,
                ]
            )

    if configs:
        click.echo("Available predefined model configurations:")
        click.echo()
        click.echo(table)
        click.echo()
        click.echo(
            "Use 'clserve serve <alias>' to serve a model with its predefined config."
        )
    else:
        click.echo("No predefined model configurations found.")


@main.command()
@click.argument("model")
@click.option(
    "--revision", "-r", type=str, default=None, help="Specific model revision/branch"
)
def download(model: str, revision: str = None):
    """Download a model from HuggingFace Hub.

    MODEL is the model name or alias (e.g., deepseek-v3, llama-405b)
    or a full HuggingFace path (e.g., meta-llama/Llama-3.1-70B-Instruct).

    Examples:

      # Download using alias
      clserve download deepseek-v3

      # Download using full path
      clserve download meta-llama/Llama-3.1-70B-Instruct

      # Download specific revision
      clserve download deepseek-v3 --revision main
    """
    from clserve.configs import get_model_path, load_model_config

    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        click.echo(
            "Error: huggingface_hub is required for downloading models", err=True
        )
        click.echo("Install it with: pip install huggingface_hub", err=True)
        raise SystemExit(1)

    # Resolve alias to full path
    model_path = get_model_path(model)

    # Show config info if using predefined config
    config = load_model_config(model)
    if config:
        click.echo(f"Downloading model: {config.model_path}")
    else:
        click.echo(f"Downloading model: {model_path}")

    try:
        path = snapshot_download(
            repo_id=model_path,
            revision=revision,
        )
        click.echo(f"Downloaded to: {path}")
    except Exception as e:
        click.echo(f"Error downloading model: {e}", err=True)
        raise SystemExit(1)


@main.command()
@click.argument("model")
def logs(model: str):
    """Show the log file path for a job.

    MODEL is the model name or alias (e.g., deepseek-v3, llama-405b).
    If multiple jobs are serving the same model, you'll be prompted to select one.

    Example:

      clserve logs deepseek-v3
      tail -f $(clserve logs deepseek-v3)/log.out
    """
    jobs = find_jobs_by_model(model)
    if not jobs:
        click.echo(f"No jobs found for model '{model}'", err=True)
        raise SystemExit(1)

    # If only one job, use it directly
    if len(jobs) == 1:
        job = jobs[0]
    else:
        # Prefer running jobs
        running = [j for j in jobs if j.state == "RUNNING"]
        if len(running) == 1:
            job = running[0]
        else:
            # Multiple jobs - use selector
            job = select_job(running if running else jobs, action="view logs")
            if job is None:
                return  # User cancelled

    log_path = CLSERVE_LOGS_DIR / job.job_id
    click.echo(log_path)


if __name__ == "__main__":
    main()
