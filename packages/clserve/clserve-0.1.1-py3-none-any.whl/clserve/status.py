"""Job status and URL retrieval for clserve."""

import os
import re
import subprocess
from dataclasses import dataclass
from typing import Optional
from pathlib import Path


# Prefix used to identify clserve jobs
CLSERVE_JOB_PREFIX = "clserve_"

# Base directory for clserve data
CLSERVE_DIR = Path(os.path.expanduser("~/.clserve"))
CLSERVE_LOGS_DIR = CLSERVE_DIR / "logs"


@dataclass
class JobInfo:
    """Information about a running or completed job."""

    job_id: str
    job_name: str
    state: str
    node_list: str
    work_dir: str
    model_path: Optional[str] = None
    endpoint_url: Optional[str] = None
    workers: Optional[int] = None
    nodes_per_worker: Optional[int] = None
    tp_size: Optional[int] = None
    dp_size: Optional[int] = None
    use_router: Optional[bool] = None


def get_my_jobs(clserve_only: bool = True) -> list[dict]:
    """Get jobs for the current user.

    Args:
        clserve_only: If True, only return jobs with clserve_ prefix

    Returns:
        List of job info dicts from squeue
    """
    try:
        result = subprocess.run(
            [
                "squeue",
                "--me",
                "--format=%i|%j|%T|%N|%Z",
                "--noheader",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return []

    jobs = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|")
        if len(parts) >= 5:
            job_name = parts[1].strip()
            # Filter to only clserve jobs if requested
            if clserve_only and not job_name.startswith(CLSERVE_JOB_PREFIX):
                continue
            jobs.append(
                {
                    "job_id": parts[0].strip(),
                    "job_name": job_name,
                    "state": parts[2].strip(),
                    "node_list": parts[3].strip(),
                    "work_dir": parts[4].strip(),
                }
            )
    return jobs


def get_job_details(job_id: str) -> Optional[dict]:
    """Get detailed information about a specific job.

    Args:
        job_id: SLURM job ID

    Returns:
        Dict with job details or None if not found
    """
    try:
        result = subprocess.run(
            ["scontrol", "show", "job", job_id],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return None

    details = {}
    for match in re.finditer(r"(\w+)=([^\s]+)", result.stdout):
        details[match.group(1)] = match.group(2)

    return details


def get_log_dir(job_id: str) -> Optional[Path]:
    """Get the log directory for a job.

    Args:
        job_id: SLURM job ID

    Returns:
        Path to log directory or None if not found
    """
    log_dir = CLSERVE_LOGS_DIR / job_id
    if log_dir.exists():
        return log_dir
    return None


def parse_metadata(log_dir: Path) -> dict:
    """Parse metadata file from log directory.

    Args:
        log_dir: Path to log directory

    Returns:
        Dict with metadata values
    """
    metadata_file = log_dir / "metadata.txt"
    if not metadata_file.exists():
        return {}

    metadata = {}
    with open(metadata_file) as f:
        for line in f:
            line = line.strip()
            if "=" in line:
                key, value = line.split("=", 1)
                metadata[key] = value
    return metadata


def extract_url_from_log(log_dir: Path) -> Optional[str]:
    """Extract endpoint URL from job logs.

    Args:
        log_dir: Path to log directory

    Returns:
        Endpoint URL or None if not found
    """
    # First try metadata file
    metadata = parse_metadata(log_dir)
    if "ENDPOINT_URL" in metadata:
        return metadata["ENDPOINT_URL"]

    # Fall back to parsing log.out
    log_file = log_dir / "log.out"
    if not log_file.exists():
        return None

    with open(log_file) as f:
        content = f.read()

    # Look for Router URL first
    router_match = re.search(r"Router URL:\s*(http://[^\s]+)", content)
    if router_match:
        return router_match.group(1)

    # Look for Endpoint URL
    endpoint_match = re.search(r"Endpoint URL:\s*(http://[^\s]+)", content)
    if endpoint_match:
        return endpoint_match.group(1)

    # Look for worker URLs
    worker_match = re.search(r"http://[\d\.]+:5000", content)
    if worker_match:
        return worker_match.group(0)

    return None


def is_clserve_job(job_name: str) -> bool:
    """Check if a job name indicates a clserve job.

    Args:
        job_name: SLURM job name

    Returns:
        True if this is a clserve job
    """
    return job_name.startswith(CLSERVE_JOB_PREFIX)


def get_job_info(job_id: str, clserve_only: bool = True) -> Optional[JobInfo]:
    """Get comprehensive information about a job.

    Args:
        job_id: SLURM job ID
        clserve_only: If True, only return info for clserve jobs

    Returns:
        JobInfo object or None if job not found or not a clserve job
    """
    details = get_job_details(job_id)
    if not details:
        return None

    job_name = details.get("JobName", "")

    # Filter non-clserve jobs if requested
    if clserve_only and not is_clserve_job(job_name):
        return None

    work_dir = details.get("WorkDir", "")
    log_dir = get_log_dir(job_id)

    # Parse metadata if available
    metadata = {}
    endpoint_url = None
    if log_dir:
        metadata = parse_metadata(log_dir)
        endpoint_url = extract_url_from_log(log_dir)

    return JobInfo(
        job_id=job_id,
        job_name=job_name,
        state=details.get("JobState", ""),
        node_list=details.get("NodeList", ""),
        work_dir=work_dir,
        model_path=metadata.get("MODEL_PATH"),
        endpoint_url=endpoint_url,
        workers=int(metadata["WORKERS"]) if "WORKERS" in metadata else None,
        nodes_per_worker=int(metadata["NODES_PER_WORKER"])
        if "NODES_PER_WORKER" in metadata
        else None,
        tp_size=int(metadata["TP_SIZE"]) if "TP_SIZE" in metadata else None,
        dp_size=int(metadata["DP_SIZE"]) if "DP_SIZE" in metadata else None,
        use_router=metadata.get("USE_ROUTER", "").lower() == "true"
        if "USE_ROUTER" in metadata
        else None,
    )


def list_serving_jobs() -> list[JobInfo]:
    """List all running serving jobs for the current user.

    Returns:
        List of JobInfo objects
    """
    jobs = get_my_jobs()
    serving_jobs = []

    for job in jobs:
        job_info = get_job_info(job["job_id"])
        if job_info:
            serving_jobs.append(job_info)

    return serving_jobs


def find_jobs_by_model(model_name: str) -> list[JobInfo]:
    """Find jobs serving a specific model.

    Args:
        model_name: Model name or path (partial match supported)

    Returns:
        List of matching JobInfo objects
    """
    jobs = list_serving_jobs()
    matches = []

    model_name_lower = model_name.lower()
    for job in jobs:
        # Check model path
        if job.model_path and model_name_lower in job.model_path.lower():
            matches.append(job)
            continue

        # Check job name
        if model_name_lower in job.job_name.lower():
            matches.append(job)
            continue

    return matches


def get_url(identifier: str) -> Optional[str]:
    """Get endpoint URL for a job by job ID or model name.

    Args:
        identifier: Job ID or model name

    Returns:
        Endpoint URL or None if not found
    """
    # Try as job ID first
    if identifier.isdigit():
        job_info = get_job_info(identifier)
        if job_info and job_info.endpoint_url:
            return job_info.endpoint_url

    # Try as model name
    matches = find_jobs_by_model(identifier)
    if matches:
        # Return URL of first running job
        for job in matches:
            if job.state == "RUNNING" and job.endpoint_url:
                return job.endpoint_url
        # Fall back to any job with URL
        for job in matches:
            if job.endpoint_url:
                return job.endpoint_url

    return None
