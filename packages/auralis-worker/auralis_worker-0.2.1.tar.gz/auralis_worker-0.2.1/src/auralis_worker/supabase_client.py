"""
Supabase Client for Worker
Handles job queries and status updates.
"""

import os
import logging
from pathlib import Path
from typing import Optional, List
from supabase import create_client, Client
from dotenv import load_dotenv

# Load .env from worker/ directory first, then try parent directory
env_file = Path(__file__).parent / ".env"
env_local_file = Path(__file__).parent.parent / ".env.local"

if env_file.exists():
    load_dotenv(env_file)
elif env_local_file.exists():
    load_dotenv(env_local_file)
else:
    load_dotenv()

logger = logging.getLogger(__name__)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

_supabase: Optional[Client] = None


def get_client() -> Client:
    """Get Supabase client instance."""
    global _supabase
    if _supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise Exception("Supabase credentials not configured")
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase


async def get_pending_jobs(compute_type: Optional[str] = None) -> List[dict]:
    """Get pending jobs, optionally filtered by compute type."""
    try:
        client = get_client()
        query = client.table("jobs").select("*").eq("status", "PENDING")
        
        if compute_type:
            query = query.eq("compute_type", compute_type)
        
        response = query.order("created_at", desc=False).limit(5).execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error fetching pending jobs: {e}")
        return []


async def get_job(job_id: str) -> Optional[dict]:
    """Get a specific job by ID."""
    try:
        client = get_client()
        response = client.table("jobs").select("*").eq("id", job_id).single().execute()
        return response.data
    except Exception as e:
        logger.error(f"Error fetching job {job_id}: {e}")
        return None


async def claim_job(job_id: str, worker_id: str) -> bool:
    """
    Attempt to claim a job for this worker.
    Uses optimistic locking - only claims if still PENDING.
    """
    try:
        client = get_client()
        
        # Update only if status is still PENDING (atomic operation)
        response = client.table("jobs").update({
            "status": "CLAIMED",
            "worker_id": worker_id
        }).eq("id", job_id).eq("status", "PENDING").execute()
        
        # Check if update was successful
        if response.data and len(response.data) > 0:
            logger.info(f"Successfully claimed job {job_id}")
            return True
        else:
            logger.info(f"Job {job_id} was already claimed by another worker")
            return False
            
    except Exception as e:
        logger.error(f"Error claiming job {job_id}: {e}")
        return False


async def update_job_status(
    job_id: str,
    status: str,
    output_url: Optional[str] = None
) -> bool:
    """Update job status and optional fields."""
    try:
        client = get_client()
        
        update_data = {"status": status}
        
        if status == "RUNNING":
            from datetime import datetime
            update_data["started_at"] = datetime.utcnow().isoformat()
        elif status in ("COMPLETED", "FAILED"):
            from datetime import datetime
            update_data["completed_at"] = datetime.utcnow().isoformat()
        
        if output_url:
            update_data["output_url"] = output_url
        
        response = client.table("jobs").update(update_data).eq("id", job_id).execute()
        return bool(response.data)
        
    except Exception as e:
        logger.error(f"Error updating job {job_id} status: {e}")
        return False


async def append_log(job_id: str, content: str) -> bool:
    """Append a log entry for a job (for real-time streaming)."""
    try:
        client = get_client()
        response = client.table("logs").insert({
            "job_id": job_id,
            "content": content
        }).execute()
        return bool(response.data)
    except Exception as e:
        logger.error(f"Error appending log for job {job_id}: {e}")
        return False


async def batch_append_logs(job_id: str, logs: List[str]) -> bool:
    """Append multiple log entries at once."""
    try:
        client = get_client()
        entries = [{"job_id": job_id, "content": log} for log in logs]
        response = client.table("logs").insert(entries).execute()
        return bool(response.data)
    except Exception as e:
        logger.error(f"Error batch appending logs for job {job_id}: {e}")
        return False
