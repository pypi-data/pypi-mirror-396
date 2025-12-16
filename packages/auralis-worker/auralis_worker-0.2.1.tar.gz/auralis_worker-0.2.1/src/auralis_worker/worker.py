"""
Auralis Worker
Core worker class that polls for pending jobs and executes them.
"""

import os
import logging
import asyncio

from .job_runner import JobRunner
from .supabase_client import get_pending_jobs, claim_job, update_job_status

logger = logging.getLogger(__name__)


class AuralisWorker:
    """Main worker class that polls and executes jobs."""
    
    def __init__(
        self,
        worker_id: str = None,
        compute_type: str = "cpu",
        poll_interval: int = 10
    ):
        self.worker_id = worker_id or f"worker-{os.getpid()}"
        self.compute_type = compute_type
        self.poll_interval = poll_interval
        self.runner = JobRunner(self.worker_id)
        self.running = True
        
    async def run_single_job(self, job_id: str) -> bool:
        """Run a specific job by ID."""
        logger.info(f"🚀 Running specific job: {job_id}")
        
        try:
            # Claim the job
            if not await claim_job(job_id, self.worker_id):
                logger.error(f"Failed to claim job {job_id}")
                return False
            
            # Execute the job
            success = await self.runner.execute_job(job_id)
            
            if success:
                logger.info(f"✅ Job {job_id} completed successfully")
            else:
                logger.error(f"❌ Job {job_id} failed")
                
            return success
            
        except Exception as e:
            logger.error(f"Error running job {job_id}: {e}")
            await update_job_status(job_id, "FAILED")
            return False
    
    async def run_polling_loop(self):
        """Main polling loop - checks for pending jobs and executes them."""
        logger.info(f"🔄 Worker {self.worker_id} starting poll loop...")
        logger.info(f"   Compute type: {self.compute_type}")
        logger.info(f"   Poll interval: {self.poll_interval}s")
        
        while self.running:
            try:
                # Get pending jobs
                jobs = await get_pending_jobs(self.compute_type)
                
                if jobs:
                    job = jobs[0]  # Take the first available job
                    job_id = job["id"]
                    logger.info(f"📋 Found pending job: {job_id}")
                    
                    # Try to claim it
                    if await claim_job(job_id, self.worker_id):
                        logger.info(f"✋ Claimed job: {job_id}")
                        
                        # Execute the job
                        try:
                            success = await self.runner.execute_job(job_id)
                            if success:
                                logger.info(f"✅ Job {job_id} completed")
                            else:
                                logger.warning(f"⚠️ Job {job_id} failed")
                        except Exception as e:
                            logger.error(f"❌ Error executing job {job_id}: {e}")
                            await update_job_status(job_id, "FAILED")
                    else:
                        logger.info(f"Job {job_id} was claimed by another worker")
                else:
                    logger.debug("No pending jobs found")
                    
            except Exception as e:
                logger.error(f"Error in poll loop: {e}")
            
            # Wait before next poll
            await asyncio.sleep(self.poll_interval)
    
    def stop(self):
        """Stop the worker."""
        self.running = False
        logger.info("Worker stopping...")
